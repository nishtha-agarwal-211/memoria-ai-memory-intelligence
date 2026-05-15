/**
 * ChatMessage Component — Individual message bubble in the chat.
 * 
 * Features:
 * - Differentiated user/AI styling with gradient borders
 * - Markdown-like bold text rendering
 * - Smooth entry animation via Framer Motion
 * - Streaming cursor for in-progress messages
 */
import { motion } from 'framer-motion';
import type { ChatMessage as ChatMessageType } from '@/lib/types';
import { Brain, User } from 'lucide-react';

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  // Simple markdown-like rendering: **bold** → <strong>
  const renderContent = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div
        className={`
          w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1
          ${isUser
            ? 'bg-gradient-to-br from-violet-500/20 to-purple-600/20 border border-violet-500/30'
            : 'bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30'
          }
        `}
      >
        {isUser ? (
          <User className="w-4 h-4 text-violet-400" />
        ) : (
          <Brain className="w-4 h-4 text-cyan-400" />
        )}
      </div>

      {/* Message Bubble */}
      <div
        className={`
          max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed
          ${isUser
            ? 'bg-gradient-to-br from-violet-500/10 to-purple-600/10 border border-violet-500/20 text-violet-50'
            : 'glass-card text-slate-200'
          }
        `}
      >
        <div className="whitespace-pre-wrap break-words">
          {renderContent(message.content)}
          {/* Streaming cursor */}
          {message.isStreaming && (
            <motion.span
              animate={{ opacity: [1, 0] }}
              transition={{ duration: 0.6, repeat: Infinity }}
              className="inline-block w-2 h-4 bg-cyan-400 ml-0.5 -mb-0.5 rounded-sm"
            />
          )}
        </div>

        {/* Timestamp */}
        <div className={`text-[10px] mt-2 ${isUser ? 'text-violet-400/50' : 'text-slate-500'}`}>
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </motion.div>
  );
}
