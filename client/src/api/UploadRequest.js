import axios from 'axios';

const API = axios.create({ baseURL: 'http://34.23.127.50' });

export const uploadImage = (data) => API.post('/upload/', data);
export const uploadPost = (data) => API.post('/post', data);