const BASE = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

async function request(path, options) {
  const isFormData = options?.body instanceof FormData;

  const headers = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...(options?.headers || {}),
  };

  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers,
  });

  let data = null;
  try {
    data = await res.json();
  } catch { }

  if (!res.ok) {
    const msg = data?.detail || data?.message || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

export const api = {
  candidateSignup: (payload) =>
    request("/auth/candidate/signup", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  candidateLogin: (payload) =>
    request("/auth/candidate/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  companySignup: (payload) =>
    request("/auth/company/signup", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  companyLogin: (payload) =>
    request("/auth/company/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listPublishedJobs: () => request("/candidate/jobs", { method: "GET" }),
  listCompanyJobs: (companyId) =>
    request(`/company/${companyId}/jobs`, { method: "GET" }),

  createJob: (payload) =>
    request("/company/job", { method: "POST", body: JSON.stringify(payload) }),

  // Candidate
  applyToJob: (formData) =>
    request("/candidate/apply", {
      method: "POST",
      body: formData // Expects FormData now
    }),

  getApplicationStatus: (applicationId) =>
    request(`/candidate/application/${applicationId}/status`, { method: "GET" }),

  submitTestResults: (applicationId, formData) =>
    request(`/candidate/application/${applicationId}/submit-test`, {
      method: "POST",
      body: formData
    }),

  getCandidateStats: (anonId) =>
    request(`/candidate/${encodeURIComponent(anonId)}/stats`, { method: "GET" }),
  listCandidateApplications: (anonId) =>
    request(`/candidate/${encodeURIComponent(anonId)}/applications`, { method: "GET" }),

  // Company
  getCompanyStats: (companyId) =>
    request(`/company/${companyId}/stats`, { method: "GET" }),
  runMatching: (companyId, jobId) =>
    request(`/company/${companyId}/jobs/${jobId}/run-matching`, { method: "POST" }),
  listJobApplications: (companyId, jobId) =>
    request(`/company/${companyId}/jobs/${jobId}/applications`, { method: "GET" }),
  listSelected: (companyId, jobId) =>
    request(`/company/${companyId}/jobs/${jobId}/selected`, { method: "GET" }),
  reviewQueue: (companyId) =>
    request(`/company/${companyId}/review-queue`, { method: "GET" }),
  reviewAction: (companyId, caseId, payload) =>
    request(`/company/${companyId}/review-queue/${caseId}/action`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Passport
  getPassport: (anonId) =>
    request(`/passport/${encodeURIComponent(anonId)}`, { method: "GET" }),
  verifyPassport: (payload) =>
    request("/passport/verify", { method: "POST", body: JSON.stringify(payload) }),

};
