const express = require('express');
const axios = require('axios');
const app = express();
const PORT = process.env.PORT || 3000;
const API_URL = process.env.API_URL; // Obtener la URL de la API desde la variable de entorno

// Configurar EJS como motor de vistas
app.set('view engine', 'ejs');

// Servir archivos estáticos
app.use(express.static('public'));

// Middleware para manejar datos de formularios
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Ruta para mostrar el input y las recomendaciones
app.get('/', (req, res) => {
    res.render('index');
});

// Ruta para manejar la obtención de recomendaciones
app.post('/recommendations', async (req, res) => {
    const userId = req.body.userId;
    const apiUrl = `${API_URL}/recommendations/${userId}`; // Usar la URL de la API desde la variable de entorno

    try {
        const response = await axios.get(apiUrl);
        const movies = response.data.recommendations;

        // Renderizar la vista de recomendaciones con las películas obtenidas
        res.render('recommendations', { movies });
    } catch (error) {
        console.error('Error al obtener las recomendaciones:', error);
        res.status(500).send('Error al obtener las recomendaciones');
    }
});

// Iniciar el servidor
app.listen(PORT, () => {
    console.log(`Servidor corriendo en el puerto ${PORT}`);
});
