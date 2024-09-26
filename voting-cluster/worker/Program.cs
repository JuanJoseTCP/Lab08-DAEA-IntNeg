using System;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using Newtonsoft.Json;
using StackExchange.Redis;
using Confluent.Kafka;

namespace Worker
{
    public class Program
    {
        public static int Main(string[] args)
        {
            try
            {
                // Obtener el host de Redis desde las variables de entorno
                var redisHost = Environment.GetEnvironmentVariable("REDIS_HOST") ?? "localhost";
                var redisConn = OpenRedisConnection(redisHost);
                var redis = redisConn.GetDatabase();

                // Obtener el host de Kafka desde las variables de entorno
                var kafkaHost = Environment.GetEnvironmentVariable("KAFKA_HOST") ?? "localhost:9092";
                var kafkaProducer = CreateKafkaProducer(kafkaHost);

                var definition = new { movie_id = "", user_id = "", rating = "" };
                
                while (true)
                {
                    // Slow down to prevent CPU spike, only query each 100ms
                    Thread.Sleep(100);

                    // Reconnect redis if down
                    if (redisConn == null || !redisConn.IsConnected)
                    {
                        Console.WriteLine("Reconnecting Redis");
                        redisConn = OpenRedisConnection(redisHost);
                        redis = redisConn.GetDatabase();
                    }

                    string json = redis.ListLeftPopAsync("votes").Result;
                    if (json != null)
                    {
                        var vote = JsonConvert.DeserializeAnonymousType(json, definition);
                        Console.WriteLine($"Processing vote for '{vote.movie_id}' by '{vote.user_id}'");

                        // Send the vote data to Kafka
                        SendToKafka(kafkaProducer, "votes-topic", vote);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine(ex.ToString());
                return 1;
            }
        }

        private static ConnectionMultiplexer OpenRedisConnection(string hostname)
        {
            var ipAddress = GetIp(hostname);
            Console.WriteLine($"Found redis at {ipAddress}");

            while (true)
            {
                try
                {
                    Console.Error.WriteLine("Connecting to redis");
                    return ConnectionMultiplexer.Connect(ipAddress);
                }
                catch (RedisConnectionException)
                {
                    Console.Error.WriteLine("Waiting for redis");
                    Thread.Sleep(1000);
                }
            }
        }

        private static string GetIp(string hostname)
            => Dns.GetHostEntryAsync(hostname)
                .Result
                .AddressList
                .First(a => a.AddressFamily == AddressFamily.InterNetwork)
                .ToString();

        private static IProducer<Null, string> CreateKafkaProducer(string kafkaHost)
        {
            var config = new ProducerConfig { BootstrapServers = kafkaHost };
            return new ProducerBuilder<Null, string>(config).Build();
        }

        private static void SendToKafka(IProducer<Null, string> producer, string topic, object voteData)
        {
            string jsonData = JsonConvert.SerializeObject(voteData);

            try
            {
                var result = producer.ProduceAsync(topic, new Message<Null, string> { Value = jsonData }).Result;
                Console.WriteLine($"Message sent to Kafka - Partition: {result.Partition}, Offset: {result.Offset}");
            }
            catch (ProduceException<Null, string> e)
            {
                Console.WriteLine($"Error sending message to Kafka: {e.Error.Reason}");
            }
        }
    }
}
