import React, { useState, useEffect, useRef } from 'react';
import styles from './styles.module.css';

const ChatWidget = ({ initialPosition = { bottom: '20px', right: '20px' } }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [selectedText, setSelectedText] = useState('');
    const messagesEndRef = useRef(null);
    const chatContainerRef = useRef(null);

    // Get API service from props or global
    const apiService = window.chatAPIService; // Assuming globally available

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Capture selected text
    useEffect(() => {
        const handleSelectionChange = () => {
            const selected = window.getSelection().toString().trim();
            setSelectedText(selected);
        };

        document.addEventListener('selectionchange', handleSelectionChange);
        return () => {
            document.removeEventListener('selectionchange', handleSelectionChange);
        };
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!inputValue.trim() || isLoading) return;

        const userMessage = {
            id: Date.now(),
            text: inputValue,
            sender: 'user',
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            let response;

            if (selectedText) {
                // Use selected text endpoint
                response = await apiService.askSelected(inputValue, selectedText);
            } else {
                // Use general endpoint
                response = await apiService.askGeneral(inputValue);
            }

            const botMessage = {
                id: Date.now() + 1,
                text: response.answer,
                sender: 'bot',
                sources: response.source_chunks || [],
                confidence: response.confidence_score,
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            console.error('Chat error:', error);

            const errorMessage = {
                id: Date.now() + 1,
                text: 'Sorry, I encountered an error processing your request.',
                sender: 'bot',
                isError: true,
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleAskAboutSelection = () => {
        if (!selectedText) return;

        setIsOpen(true);  // Open chat if closed
        setInputValue('');  // Clear input
        // Focus on input and add selection hint
        setTimeout(() => {
            const inputElement = document.querySelector(`.${styles['chat-input']}`);
            if (inputElement) {
                inputElement.focus();
                inputElement.placeholder = `Ask about: "${selectedText.substring(0, 30)}..."`;
            }
        }, 100);
    };

    const clearChat = () => {
        setMessages([]);
    };

    return (
        <div
            className={styles['chat-widget-container']}
            style={initialPosition}
            ref={chatContainerRef}
        >
            {/* Selection indicator */}
            {selectedText && (
                <button
                    className={styles['ask-selection-btn']}
                    onClick={handleAskAboutSelection}
                    title={`Ask about: "${selectedText.substring(0, 30)}${selectedText.length > 30 ? '...' : ''}"`}
                >
                    💬 Ask about selection
                </button>
            )}

            {/* Chat toggle button */}
            {!isOpen && (
                <button
                    className={styles['chat-toggle']}
                    onClick={() => setIsOpen(true)}
                >
                    🤖
                </button>
            )}

            {/* Chat window */}
            {isOpen && (
                <div className={styles['chatWindow']}>
                    <div className={styles['chatHeader']}>
                        <h3>Ask the Book Assistant</h3>
                        <button
                          onClick={() => setIsOpen(false)}
                          className={styles['closeBtn']}
                        >
                          ✕
                        </button>
                    </div>

                    <div className={styles['chatMessages']}>
                        {messages.map((msg) => (
                            <div
                                key={msg.id}
                                className={`${styles['message']} ${styles[msg.sender]}`}
                                title={`Confidence: ${msg.confidence || 'N/A'}`}
                            >
                                {msg.sender === 'bot' && msg.sources && msg.sources.length > 0 && (
                                    <div className={styles['sources']}>
                                        <small>Sources: {msg.sources.slice(0, 2).join(', ')}</small>
                                    </div>
                                )}
                                <p>{msg.text}</p>
                                {msg.isError && (
                                    <small className={styles['errorText']}>⚠️ Error occurred - please try again</small>
                                )}
                            </div>
                        ))}
                        {isLoading && (
                            <div className={`${styles['message']} ${styles['bot']}`}>
                                <p>...thinking</p>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <form onSubmit={handleSubmit} className={styles['chatInputForm']}>
                        <input
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            placeholder={selectedText ? "Ask about selected text..." : "Ask about the book..."}
                            className={styles['chatInput']}
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={!inputValue.trim() || isLoading}
                            className={styles['sendButton']}
                        >
                            {isLoading ? ' Sending...' : 'Send'}
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
};

export default ChatWidget;