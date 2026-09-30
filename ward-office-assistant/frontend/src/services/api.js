import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
  headers: { "Content-Type": "application/json" },
});

// TODO: once JWT auth exists, attach the token here via an interceptor:
// apiClient.interceptors.request.use((config) => {
//   const token = localStorage.getItem("access_token");
//   if (token) config.headers.Authorization = `Bearer ${token}`;
//   return config;
// });

export async function askQuestion({ question, sessionId, serviceId }) {
  const { data } = await apiClient.post("/chat/", {
    question,
    session_id: sessionId ?? null,
    service_id: serviceId ?? null,
  });
  return data; // { answer, sources, detected_language }
}

export async function listServices() {
  const { data } = await apiClient.get("/services/");
  return data;
}

export async function getService(serviceId) {
  const { data } = await apiClient.get(`/services/${serviceId}`);
  return data;
}

export async function getNextChecklistStep({ serviceId, answers }) {
  const { data } = await apiClient.post("/services/checklist", {
    service_id: serviceId,
    answers,
  });
  return data; // { next_question, checklist, is_complete }
}

export async function checkDocumentReadiness({ serviceId, files }) {
  const formData = new FormData();
  formData.append("service_id", serviceId);
  files.forEach((file) => formData.append("files", file));

  const { data } = await apiClient.post("/documents/readiness-check", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data; // { overall_ready, checks, notes }
}

// TODO: add getOfficeInfo() once GET /services/office-info exists on the backend.

export default apiClient;
