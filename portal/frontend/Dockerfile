FROM node:14.21.1-alpine

ENV CONTAINER_PATH /frontend

WORKDIR $CONTAINER_PATH

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 8080

CMD ["npm", "run", "build"]
# CMD ["npm", "run", "serve"]

