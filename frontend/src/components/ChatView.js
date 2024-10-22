import React, { useState, useEffect, useCallback } from 'react';
import debounce from 'lodash/debounce';

const ChatView = ({ contact }) => {
  const [messages, setMessages] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [error, setError] = useState(null);

  const fetchMessages = useCallback(async (reset = false) => {
    try {
      const currentPage = reset ? 1 : page;
      const url = new URL(`http://localhost:5000/api/chat/${contact.id}`);
      url.searchParams.append('page', currentPage);
      url.searchParams.append('search', searchQuery);
      if (startDate) url.searchParams.append('start_date', startDate);
      if (endDate) url.searchParams.append('end_date', endDate);

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch messages');
      }
      const data = await response.json();
      setMessages(prevMessages => reset ? data.messages : [...prevMessages, ...data.messages]);
      setHasMore(data.has_next);
      setPage(prevPage => reset ? 2 : prevPage + 1);
      setError(null);
    } catch (err) {
      setError('Failed to load messages. Please try again.');
      console.error('Error fetching messages:', err);
    }
  }, [contact.id, page, searchQuery, startDate, endDate]);

  useEffect(() => {
    setMessages([]);
    setPage(1);
    setHasMore(true);
    fetchMessages(true);
  }, [contact, searchQuery, startDate, endDate, fetchMessages]);

  const debouncedSearch = useCallback(
    debounce((value) => {
      setSearchQuery(value);
    }, 300),
    []
  );

  const handleSearch = (e) => {
    debouncedSearch(e.target.value);
  };

  const handleDateChange = (e) => {
    const { name, value } = e.target;
    if (name === 'start_date') {
      setStartDate(value);
    } else if (name === 'end_date') {
      setEndDate(value);
    }
  };

  return (
    <div className="chat-view">
      <h2>{contact.name}</h2>
      <div className="search-container">
        <input
          type="text"
          placeholder="Search messages..."
          onChange={handleSearch}
        />
        <input
          type="date"
          name="start_date"
          onChange={handleDateChange}
          placeholder="Start Date"
        />
        <input
          type="date"
          name="end_date"
          onChange={handleDateChange}
          placeholder="End Date"
        />
      </div>
      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => fetchMessages(true)} disabled={!error}>Retry</button>
        </div>
      )}
      <div className="messages">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.sender === contact.id ? 'received' : 'sent'}`}>
            <p>{message.text}</p>
            <span className="timestamp">{new Date(message.time).toLocaleString()}</span>
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
