import React, { useState, useRef, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { FiSend, FiUser } from 'react-icons/fi';
import axios from 'axios';
import logo from './assets/cloudnine-logo.svg';
import robotAvatar from './assets/robot-avatar.svg';
import {
  Container,
  Header,
  Logo,
  Title,
  ChatContainer,
  MessageWrapper,
  Avatar,
  MessageBubble,
  InputContainer,
  Input,
  SendButton,
  TypingIndicator
} from './styles';

function App() {
  const [messages, setMessages] = useState([{
    text: "Hello! I'm your CloudNine Healthcare Assistant. How can I help you today?",
    isUser: false
  }]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    const container = document.querySelector('.chat-container');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);
    setIsTyping(true);

    try {
      const response = await axios.post('http://localhost:8000/chat', {
        message: userMessage,
        session_id: localStorage.getItem('sessionId') || 'new_session'
      });

      if (response.data.session_id) {
        localStorage.setItem('sessionId', response.data.session_id);
      }

      setTimeout(() => {
        setIsTyping(false);
        setMessages(prev => [...prev, { text: response.data.response, isUser: false }]);
      }, 500);
    } catch (error) {
      console.error('Error:', error);
      setIsTyping(false);
      setMessages(prev => [...prev, { 
        text: 'Sorry, I encountered an error. Please try again.', 
        isUser: false 
      }]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Container>
      <Header>
        <Logo src={logo} alt="CloudNine Logo" />
        <Title>CloudNine Healthcare Assistant</Title>
      </Header>
      
      <ChatContainer
        className="chat-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <AnimatePresence>
          {messages.map((message, index) => (
            <MessageWrapper
              key={index}
              isUser={message.isUser}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Avatar isUser={message.isUser}>
                {message.isUser ? <FiUser /> : <img src={robotAvatar} alt="Assistant" style={{ width: '100%', height: '100%' }} />}
              </Avatar>
              <MessageBubble isUser={message.isUser}>
                {message.text}
              </MessageBubble>
            </MessageWrapper>
          ))}
          {isTyping && (
            <MessageWrapper>
              <Avatar>
                <img src={robotAvatar} alt="Assistant" style={{ width: '100%', height: '100%' }} />
              </Avatar>
              <TypingIndicator
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <span />
                <span />
                <span />
              </TypingIndicator>
            </MessageWrapper>
          )}
        </AnimatePresence>
      </ChatContainer>

      <InputContainer>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={isTyping}
        />
        <SendButton
          onClick={handleSend}
          disabled={!input.trim() || isTyping}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <FiSend />
          Send
        </SendButton>
      </InputContainer>
    </Container>
  );
}

export default App;