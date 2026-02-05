import config from "./config";

export async function fetchAPI<T>(url: string, data?: any): Promise<T> {
  let options = {} as RequestInit;

  if (data) {
    options = {
      ...options,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    };
  }
  const response = await fetch(`${config.BACKEND_URL}${url}`, options);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  const out = await response.json();
  return out;
}
