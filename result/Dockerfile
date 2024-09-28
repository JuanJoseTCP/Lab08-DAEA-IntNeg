FROM node:16

# Crear un directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el package.json y package-lock.json
COPY package*.json ./

# Instalar las dependencias
RUN npm install

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto que utiliza la aplicación
EXPOSE 3000

# Iniciar la aplicación
CMD ["npm", "start"]
