import React, { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";
import { getAIMessage } from "../api/api";
import { marked } from "marked";

function ChatWindow() {
  const defaultPrompts = [
    "Find a dishwasher rack wheel",
    "Is PS11752778 compatible with WDT780SAEM1?",
    "My refrigerator ice maker is not working",
    "How do I install PS11752778?",
  ];

  const defaultMessage = [
    {
      role: "assistant",
      content:
        "Hi! I can help you find refrigerator and dishwasher parts, check compatibility, troubleshoot common issues, and provide installation guidance.",
      data: null,
      intent: null,
    },
  ];

  const [messages, setMessages] = useState(defaultMessage);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const getSuggestedPrompts = (latestUserText = "") => {
    const text = latestUserText.toLowerCase().trim();

    if (!text) {
      return defaultPrompts;
    }

    if (text.includes("refrigerator") || text.includes("fridge")) {
      return [
        "Show me an ice maker",
        "My refrigerator is not cooling",
        "Do you have a refrigerator door gasket?",
        "Water dispenser not working",
      ];
    }

    if (text.includes("dishwasher")) {
      return [
        "Show me a dishwasher drain pump",
        "Dishwasher leaking",
        "Dishwasher not draining",
        "Do you sell replacement wheels?",
      ];
    }

    if (
      text.includes("compatible") ||
      text.includes("fit") ||
      text.includes("model")
    ) {
      return [
        "How do I install PS11752778?",
        "Find a dishwasher rack wheel",
        "Show me refrigerator parts",
        "My dishwasher is leaking",
      ];
    }

    if (
      text.includes("not working") ||
      text.includes("leaking") ||
      text.includes("not cooling") ||
      text.includes("broken") ||
      text.includes("not draining")
    ) {
      return [
        "Show me the recommended parts",
        "How do I install PS11752778?",
        "Check compatibility for WDT780SAEM1",
        "Find refrigerator parts",
      ];
    }

    if (text.includes("install") || text.includes("replace")) {
      return [
        "Check compatibility for PS11752778 and WDT780SAEM1",
        "Find a dishwasher rack wheel",
        "My refrigerator ice maker is not working",
        "Show me refrigerator door gaskets",
      ];
    }

    if (
      text.includes("ice maker") ||
      text.includes("wheel") ||
      text.includes("gasket") ||
      text.includes("pump") ||
      text.includes("part")
    ) {
      return [
        "Is PS11752778 compatible with WDT780SAEM1?",
        "How do I install PS11752778?",
        "Find refrigerator parts",
        "Find dishwasher parts",
      ];
    }

    return defaultPrompts;
  };

  const handleSend = async (messageText) => {
    const trimmedInput = messageText.trim();

    if (!trimmedInput || isLoading) {
      return;
    }

    setMessages((prevMessages) => [
      ...prevMessages,
      { role: "user", content: trimmedInput },
    ]);
    setInput("");
    setIsLoading(true);

    const newMessage = await getAIMessage(trimmedInput);

    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setIsLoading(false);
  };

  const renderStars = (rating = 0) => {
    const rounded = Math.round(rating);
    return "★".repeat(rounded) + "☆".repeat(5 - rounded);
  };

  const renderProductCards = (message) => {
    if (
      message.role !== "assistant" ||
      message.intent !== "search" ||
      !Array.isArray(message.data) ||
      message.data.length === 0
    ) {
      return null;
    }

    return (
      <div className="product-cards">
        {message.data.map((item, index) => (
          <div key={index} className="product-card">
            <div className="product-card-top">
              <div className="product-badge">{item.appliance}</div>
              <div className="product-price">${item.price}</div>
            </div>

            <div className="product-title">{item.name}</div>
            <div className="product-part-number">{item.part_number}</div>

            <div className="product-rating-row">
              <span className="stars">{renderStars(item.rating)}</span>
              <span className="rating-text">
                {item.rating} ({item.review_count} reviews)
              </span>
            </div>

            <div className="product-description">{item.description}</div>

            {item.review_snippets?.length > 0 && (
              <div className="review-snippet">
                “{item.review_snippets[0]}”
              </div>
            )}

            <div className="product-meta">
              <span>{item.brand}</span>
              <span>OEM replacement part</span>
            </div>

            <div className="product-actions">
              <button
                className="card-button primary"
                onClick={() =>
                  handleSend(
                    `Is ${item.part_number} compatible with WDT780SAEM1?`
                  )
                }
                disabled={isLoading}
              >
                Check compatibility
              </button>

              <button
                className="card-button secondary"
                onClick={() => handleSend(`How do I install ${item.part_number}?`)}
                disabled={isLoading}
              >
                Install guide
              </button>

              <button
                className="card-button partselect"
                onClick={() =>
                  window.open(
                    `https://www.partselect.com/`,
                    "_blank",
                    "noopener,noreferrer"
                  )
                }
              >
                View on PartSelect
              </button>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderFollowUpPrompts = (message, index) => {
    const isLastMessage = index === messages.length - 1;

    if (!isLastMessage || message.role !== "assistant" || isLoading) {
      return null;
    }

    const latestUserMessage = [...messages]
      .slice(0, index + 1)
      .reverse()
      .find((msg) => msg.role === "user");

    const prompts = getSuggestedPrompts(latestUserMessage?.content || "");

    return (
      <div className="follow-up-prompts">
        {prompts.map((prompt, promptIndex) => (
          <button
            key={promptIndex}
            className="prompt-chip"
            onClick={() => handleSend(prompt)}
            disabled={isLoading}
          >
            {prompt}
          </button>
        ))}
      </div>
    );
  };

  return (
    <div className="messages-shell">
      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`${message.role}-message-container`}>
            {message.content && (
              <div className={`message ${message.role}-message`}>
                <div
                  dangerouslySetInnerHTML={{
                    __html: marked(message.content).replace(/<p>|<\/p>/g, ""),
                  }}
                />
              </div>
            )}

            {renderProductCards(message)}
            {renderFollowUpPrompts(message, index)}
          </div>
        ))}

        {isLoading && (
          <div className="assistant-message-container">
            <div className="message assistant-message">Thinking...</div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about a part, model number, compatibility, or appliance issue..."
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend(input);
            }
          }}
        />
        <button
          className="send-button"
          onClick={() => handleSend(input)}
          disabled={isLoading}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;