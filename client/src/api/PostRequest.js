import axios from 'axios';

const API = axios.create({ baseURL: 'http://34.23.127.50' });

export const getTimelinePosts = (id) => API.get(`/post/${id}/timeline`);
export const likePost = (id, userId) => API.put(`post/${id}/like_dislike`, { userId: userId })