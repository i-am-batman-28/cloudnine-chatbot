import styled from 'styled-components';
import { motion } from 'framer-motion';

export const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
`;

export const Header = styled.header`
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(124, 58, 237, 0.1);
  backdrop-filter: blur(10px);
`;

export const Logo = styled.img`
  height: 50px;
  width: 50px;
  animation: float 3s ease-in-out infinite;
  
  @keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
  }
`;

export const Title = styled.h1`
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

export const ChatContainer = styled(motion.div)`
  flex: 1;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(124, 58, 237, 0.1);
  backdrop-filter: blur(10px);
  
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05);
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(124, 58, 237, 0.5);
    border-radius: 3px;
  }
`;

export const MessageWrapper = styled(motion.div)`
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  ${props => props.isUser ? 'flex-direction: row-reverse;' : ''}
`;

export const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props => props.isUser ? 
    'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' : 
    'white'
  };
  box-shadow: 0 4px 6px rgba(124, 58, 237, 0.2);
  color: ${props => props.isUser ? 'white' : '#7c3aed'};
`;

export const MessageBubble = styled.div`
  background: ${props => props.isUser ? 
    'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' : 
    'white'
  };
  color: ${props => props.isUser ? 'white' : '#1a1a1a'};
  padding: 1rem 1.5rem;
  border-radius: 1rem;
  ${props => props.isUser ? 
    'border-bottom-right-radius: 0.25rem;' : 
    'border-bottom-left-radius: 0.25rem;'
  }
  max-width: 70%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  line-height: 1.5;
`;

export const InputContainer = styled.div`
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(124, 58, 237, 0.1);
  margin-top: 1rem;
`;

export const Input = styled.input`
  flex: 1;
  border: 2px solid rgba(124, 58, 237, 0.2);
  border-radius: 0.75rem;
  padding: 1rem 1.5rem;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
  
  &:focus {
    border-color: #7c3aed;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2);
  }
`;

export const SendButton = styled(motion.button)`
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
  border: none;
  border-radius: 0.75rem;
  padding: 1rem 1.5rem;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(124, 58, 237, 0.3);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

export const TypingIndicator = styled(motion.div)`
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  
  span {
    width: 8px;
    height: 8px;
    background: #7c3aed;
    border-radius: 50%;
    animation: bounce 1s infinite;
    
    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
  
  @keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
  }
`;