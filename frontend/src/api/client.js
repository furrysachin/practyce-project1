/**
 * API client for Retail Banking Transaction Analytics backend.
 * Base URL: same origin when using proxy (package.json proxy -> http://localhost:8000)
 */
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || '/api';

const client = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
});

export async function uploadJsonFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await client.post('/upload/json', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function getFileSummary(batchId) {
  const { data } = await client.get(`/summary/file/${batchId}`);
  return data;
}

export async function getOverallSummary() {
  const { data } = await client.get('/summary/overall');
  return data;
}

export async function getBatches() {
  const { data } = await client.get('/summary/batches');
  return data;
}

export async function getTransactionsPerFile() {
  const { data } = await client.get('/summary/transactions-per-file');
  return data;
}
