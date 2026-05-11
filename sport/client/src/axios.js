import axios from 'axios';

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  // withCredentials: true,  // УБРАТЬ для Token auth
});

// Автоматически добавляем токен к каждому запросу
instance.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Token ${token}`;
  }
  return config;
});

// Обработка ошибок авторизации
instance.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      // Если ошибка авторизации - очищаем токен и редиректим на логин
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Редирект только если не на странице логина
      if (!window.location.pathname.includes('/login') && 
          window.location.pathname !== '/') {
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

export default instance;