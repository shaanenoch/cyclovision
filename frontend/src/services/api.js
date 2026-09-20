import axios from 'axios';

// In development with Vite proxy, requests to /api, /uploads, /data map to http://127.0.0.1:8000
const API_BASE = '';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export const api = {
  // Health
  getHealth: () => apiClient.get('/api/health').then(res => res.data),

  // Cyclones & Search
  getCyclones: () => apiClient.get('/api/cyclones').then(res => res.data),
  getCycloneDetails: (id) => apiClient.get(`/api/cyclones/${id}`).then(res => res.data),
  search: (query) => apiClient.get(`/api/search?q=${encodeURIComponent(query)}`).then(res => res.data),

  // Analysis & Prediction
  analyzeCyclone: (formData) => 
    apiClient.post('/api/analyze', formData).then(res => res.data),

  detectCyclone: (formData) => 
    apiClient.post('/api/detect', formData).then(res => res.data),

  classifyCyclone: (formData) => 
    apiClient.post('/api/classify', formData).then(res => res.data),

  predictTrack: (payload) => apiClient.post('/api/predict-track', payload).then(res => res.data),
  predictIntensity: (wind, pres) => 
    apiClient.post(`/api/predict-intensity?current_wind_kmph=${wind}&current_pressure_hpa=${pres}`).then(res => res.data),

  // Datasets
  uploadDataset: (formData) =>
    apiClient.post('/api/datasets/upload', formData).then(res => res.data),
  
  getDatasets: () => apiClient.get('/api/datasets').then(res => res.data),
  analyzeDataset: (id) => apiClient.post(`/api/datasets/${id}/analyze`).then(res => res.data),

  // Model Analytics
  getModelMetrics: () => apiClient.get('/api/model/metrics').then(res => res.data),
  trainModel: () => apiClient.post('/api/model/train').then(res => res.data),
};

export default api;
