import React, { useState, useEffect } from 'react';
import ChatStatistics from './ChatStatistics';

const ChatView = ({ contact }) => {
  const [messages, setMessages] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchMessages = async (reset = false) => {
    const currentPage = reset ? 1 : page;
    const response = await fetch(`http://localhost:5000/api/chat/${contact.id}?page=${currentPage}&search=${searchQuery}`);
    const data = await response.json();
    setMessages(prevMessages => reset ? data.messages : [...prevMessages, ...data.messages]);
    setHasMore(data.has_next);
    setPage(prevPage => reset ? 2 : prevPage + 1);
  };

  useEffect(() => {
    setMessages([]);
    setPage(1);
    setHasMore(true);
    fetchMessages(true);
  }, [contact, searchQuery]);

  const handleSearch = (e) => {
    setSearchQuery(e.target.value);
  };

  return (
    <div className="chat-view">
      <h2>{contact.name}</h2>
      <ChatStatistics contactId={contact.id} />
      <input
        type="text"
        placeholder="Search messages..."
        value={searchQuery}
        onChange={handleSearch}
        className="search-input"
      />
      <div className="messages">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.sender_id === contact.id ? 'received' : 'sent'}`}>
            <p>{message.content}</p>
            <span className="timestamp">{new Date(message.timestamp).toLocaleString()}</span>
          </div>
        ))}
      </div>
      {hasMore && (
        <button onClick={() => fetchMessages()} className="load-more">
          Load More
        </button>
      )}
    </div>
  );
};

export default ChatView;
