import React, { useState, useEffect } from 'react';
import SearchBar from './SearchBar';

const ContactList = ({ onSelectContact }) => {
  const [contacts, setContacts] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState(null);

  const fetchContacts = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/contacts?page=${page}&search=${searchQuery}`);
      if (!response.ok) {
        throw new Error('Failed to fetch contacts');
      }
      const data = await response.json();
      setContacts(prevContacts => [...prevContacts, ...data.contacts]);
      setHasMore(data.has_next);
      setPage(prevPage => prevPage + 1);
      setError(null);
    } catch (err) {
      setError('Failed to load contacts. Please try again.');
      console.error('Error fetching contacts:', err);
    }
  };

  useEffect(() => {
    setContacts([]);
    setPage(1);
    setHasMore(true);
    fetchContacts();
  }, [searchQuery]);

  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  return (
    <div className="contact-list">
      <SearchBar onSearch={handleSearch} />
      {error && (
        <div className="error-message">
          {error}
          <button onClick={fetchContacts} disabled={!error}>Retry</button>
        </div>
      )}
      {contacts.map(contact => (
        <div key={contact.id} className="contact-item" onClick={() => onSelectContact(contact)}>
          <img src={`https://i.pravatar.cc/50?u=${contact.id}`} alt={contact.name} className="avatar" />
          <div className="contact-info">
            <h3>{contact.name}</h3>
            <p>{contact.last_message}</p>
          </div>
          <span className="timestamp">{new Date(contact.last_message_time).toLocaleString()}</span>
        </div>
      ))}
      {hasMore && (
        <button onClick={fetchContacts} className="load-more">
          Load More
        </button>
      )}
    </div>
  );
};

export default ContactList;
