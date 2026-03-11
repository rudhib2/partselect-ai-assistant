export const getAIMessage = async (userQuery) => {
  try {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: userQuery,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch response from backend");
    }

    const data = await response.json();

    return {
      role: "assistant",
      content: data.answer || "Sorry, I could not generate a response.",
      data: data.data ?? null,
      intent: data.intent ?? null,
    };
  } catch (error) {
    return {
      role: "assistant",
      content: "Sorry — I ran into an error while contacting the backend.",
      data: null,
      intent: null,
    };
  }
};

export const getInsightsSummary = async () => {
  try {
    const response = await fetch("http://127.0.0.1:8000/insights-summary");

    if (!response.ok) {
      throw new Error("Failed to fetch insights summary");
    }

    return await response.json();
  } catch (error) {
    console.error("Insights fetch failed:", error);
    return null;
  }
};