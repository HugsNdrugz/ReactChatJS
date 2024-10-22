import React, { useState, useEffect } from 'react';
import ChatStatistics from './ChatStatistics';

const ChatView = ({ contact }) => {
  const [messages, setMessages] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const fetchMessages = async () => {
    const response = await fetch(`http://localhost:5000/api/chat/${contact.id}?page=${page}`);
    const data = await response.json();
    setMessages(prevMessages => [...data.messages.reverse(), ...prevMessages]);
    setHasMore(data.has_next);
    setPage(prevPage => prevPage + 1);
  };

  useEffect(() => {
    setMessages([]);
    setPage(1);
    setHasMore(true);
    fetchMessages();
  }, [contact]);

  return (
    <div className="chat-view">
      <h2>{contact.name}</h2>
      <ChatStatistics contactId={contact.id} />
      {hasMore && (
        <button onClick={fetchMessages} className="load-more">
          Load More
        </button>
      )}
      <div className="messages">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.sender_id === contact.id ? 'received' : 'sent'}`}>
            <p>{message.content}</p>
            <span className="timestamp">{new Date(message.timestamp).toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatView;
