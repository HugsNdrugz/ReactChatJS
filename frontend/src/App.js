import React, { useState } from 'react';
import ContactList from './components/ContactList';
import ChatView from './components/ChatView';
import './App.css';

function App() {
  const [selectedContact, setSelectedContact] = useState(null);

  return (
    <div className="app">
      <div className="sidebar">
        <ContactList onSelectContact={setSelectedContact} />
      </div>
      <div className="main-content">
        {selectedContact ? (
          <ChatView contact={selectedContact} />
        ) : (
          <div className="welcome-message">
            <h2>Welcome to Facebook Messenger Clone</h2>
            <p>Select a contact to start chatting</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
