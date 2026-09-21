const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const getToken = () => {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem("nexus_access_token");
};

const getAuthHeaders = (): Record<string, string> => {
  const token = getToken();

  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
};

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (response.status === 401) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("nexus_access_token");
      localStorage.removeItem("nexus_user");
      window.location.href = "/login";
    }

    throw new Error("Your session has expired. Please login again.");
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      typeof data?.detail === "string"
        ? data.detail
        : typeof data?.message === "string"
          ? data.message
          : "Something went wrong.";

    throw new Error(detail);
  }

  return data as T;
};

// --------------------------------------------------
// CONVERSATIONS
// --------------------------------------------------

export const createConversation = async () => {
  const response = await fetch(`${API_URL}/conversations`, {
    method: "POST",
    headers: getAuthHeaders(),
  });

  return handleResponse(response);
};

export const getConversations = async () => {
  const response = await fetch(`${API_URL}/conversations`, {
    headers: getAuthHeaders(),
  });

  return handleResponse(response);
};

export const getConversationMessages = async (conversationId: number) => {
  const response = await fetch(
    `${API_URL}/conversations/${conversationId}/messages`,
    {
      headers: getAuthHeaders(),
    },
  );

  return handleResponse(response);
};

export const deleteConversation = async (conversationId: number) => {
  const response = await fetch(`${API_URL}/conversations/${conversationId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  return handleResponse(response);
};

// --------------------------------------------------
// CHAT
// --------------------------------------------------

export const sendChatMessage = async (
  question: string,
  conversationId: number,
) => {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify({
      question,
      conversation_id: conversationId,
    }),
  });

  return handleResponse(response);
};

// --------------------------------------------------
// DOCUMENTS
// --------------------------------------------------

export const uploadDocument = async (file: File) => {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(`${API_URL}/documents/upload`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: formData,
  });

  return handleResponse(response);
};

// --------------------------------------------------
// AUTH
// --------------------------------------------------

export const logout = () => {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.removeItem("nexus_access_token");
  localStorage.removeItem("nexus_user");

  window.location.href = "/login";
};
