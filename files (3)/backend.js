const BASE = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

async function request(path, options) {
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
    ...options,
  });

  let data = null;
  try {
    data = await res.json();
  } catch {}

  if (!res.ok) {
    const msg = data?.detail || data?.message || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

async function requestMultipart(path, formData) {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    body: formData,
    // Don't set Content-Type header - let browser set it with boundary
  });

  let data = null;
  try {
    data = await res.json();
  } catch {}

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

  // Candidate - NEW: File upload support
  applyToJobWithFiles: (formData) =>
    requestMultipart("/candidate/apply", formData),

  // Candidate - Application status polling
  getApplicationStatus: (applicationId) =>
    request(`/candidate/application/${applicationId}/status`, { method: "GET" }),

  // Candidate - Test submission
  submitTest: (applicationId, testScore, testData) => {
    const formData = new FormData();
    formData.append('test_score', testScore);
    if (testData) {
      formData.append('test_data', JSON.stringify(testData));
    }
    return requestMultipart(`/candidate/application/${applicationId}/submit-test`, formData);
  },

  // Legacy support (will be removed)
  applyToJob: (payload) =>
    request("/candidate/apply", { method: "POST", body: JSON.stringify(payload) }),

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
