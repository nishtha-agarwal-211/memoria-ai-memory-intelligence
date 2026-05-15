/**
 * ChatInput Component — Message input bar with send button.
 * 
 * Features:
 * - Glassmorphic styling
 * - Submit on Enter (Shift+Enter for newline)
 * - Animated send button with loading state
 * - Auto-resize textarea
 */
import { useState, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = useCallback(() => {
    if (value.trim() && !isLoading) {
      onSend(value.trim());
      setValue('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  }, [value, isLoading, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    // Auto-resize
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
  };

  return (
    <div className="p-4 border-t border-[var(--color-border)]">
      <div className="glass-card flex items-end gap-2 p-2 !rounded-xl">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask me anything... I'll use my memories to help."
          disabled={isLoading}
          rows={1}
          className="
            flex-1 bg-transparent border-none outline-none resize-none
            text-sm text-slate-200 placeholder:text-slate-500
            px-3 py-2 max-h-[120px]
            font-[var(--font-sans)]
          "
        />
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleSubmit}
          disabled={!value.trim() || isLoading}
          className="
            w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0
            bg-gradient-to-r from-cyan-500 to-blue-500
            disabled:opacity-30 disabled:cursor-not-allowed
            transition-all duration-200
            hover:shadow-[0_0_20px_rgba(34,211,238,0.3)]
          "
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 text-white animate-spin" />
          ) : (
            <Send className="w-4 h-4 text-white" />
          )}
        </motion.button>
      </div>
    </div>
  );
}
