import React, { useState, useRef, useEffect } from 'react';
import {
  MessageSquare,
  Send,
  ShieldCheck,
  Smartphone,
  Sparkles,
  Bot,
  User,
  CheckCheck,
  AlertTriangle,
  FileText,
} from 'lucide-react';
import api from '../services/api';

const QUICK_PROMPTS = [
  'MRP was 150 but store charged 180 at Bandra',
  'दुकानदार ने एमआरपी से 50 रुपये ज्यादा लिया और बिल नहीं दिया',
  'Dual sticker pasted over printed price on olive oil',
  'Missing customer care contact on packaged pulses',
];

export default function CitizenBotSimulatorPage() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: 'Namaste! 🙏 Welcome to the National Legal Metrology Consumer Assistant.\n\nYou can report overcharging above MRP, dual sticker tampering, or missing statutory declarations directly in English or Hindi.',
      time: '10:00 AM',
      isViolation: false,
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [phone, setPhone] = useState('+91 98765 43210');
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSendMessage = async (textToSend) => {
    const query = textToSend || inputText;
    if (!query.trim() || loading) return;

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: query,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setLoading(true);

    try {
      const resp = await api.post('/citizen/bot/webhook', {
        sender_phone: phone,
        sender_name: 'Simulated Citizen',
        message_text: query,
        platform: 'WHATSAPP',
      });

      const botMsg = {
        id: Date.now() + 1,
        sender: 'bot',
        text: resp.data.reply_text,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isViolation: resp.data.is_violation_identified,
        ticket: resp.data.auto_generated_ticket_number,
        statutoryRef: resp.data.statutory_reference,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errorMsg = {
        id: Date.now() + 1,
        sender: 'bot',
        text: 'Sorry, we are unable to process your report at this moment. Please check your internet connection.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isViolation: false,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold uppercase tracking-wider">
            <MessageSquare className="w-3.5 h-3.5" />
            Conversational Consumer Bot
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            WhatsApp & Telegram Citizen Enforcement Bot
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm max-w-xl mx-auto">
            Simulate how Indian citizens report retail packaging infractions over instant messaging with automated AI parsing and grievance ticket creation.
          </p>
        </div>

        {/* Smartphone Shell Mockup */}
        <div className="max-w-md mx-auto bg-slate-900 border-4 border-slate-800 rounded-[32px] overflow-hidden shadow-2xl flex flex-col h-[640px]">
          {/* WhatsApp Header */}
          <div className="bg-emerald-800 text-white p-3.5 flex items-center gap-3 shrink-0 shadow-md">
            <div className="w-10 h-10 rounded-full bg-emerald-950 border border-emerald-400/50 flex items-center justify-center font-bold text-emerald-400 text-sm shrink-0">
              <Bot className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5">
                <h3 className="font-bold text-sm truncate">Legal Metrology Dept</h3>
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-300 shrink-0" />
              </div>
              <p className="text-[11px] text-emerald-200 truncate">Official Govt of India Bot • Online</p>
            </div>
          </div>

          {/* Chat Messages Body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-950/70">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl p-3 text-xs leading-relaxed ${
                    m.sender === 'user'
                      ? 'bg-emerald-600 text-white rounded-br-none'
                      : m.isViolation
                      ? 'bg-slate-900 border border-amber-500/40 text-slate-100 rounded-bl-none'
                      : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none'
                  }`}
                >
                  <p className="whitespace-pre-line">{m.text}</p>

                  {m.ticket && (
                    <div className="mt-2 pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] text-emerald-400 font-mono">
                      <span>Ticket: {m.ticket}</span>
                      <CheckCheck className="w-3.5 h-3.5" />
                    </div>
                  )}

                  <div
                    className={`text-[9px] mt-1 text-right ${
                      m.sender === 'user' ? 'text-emerald-200' : 'text-slate-500'
                    }`}
                  >
                    {m.time}
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 p-2.5 rounded-2xl rounded-bl-none text-xs text-slate-400 w-fit">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce"></span>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce delay-100"></span>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce delay-200"></span>
                <span className="text-[10px] ml-1">Analyzing statutory rules...</span>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Quick Prompts */}
          <div className="p-2 bg-slate-900/90 border-t border-slate-800 flex gap-1.5 overflow-x-auto text-[10px] shrink-0 no-scrollbar">
            {QUICK_PROMPTS.map((p, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(p)}
                className="px-2.5 py-1 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 whitespace-nowrap transition-colors border border-slate-700"
              >
                {p.length > 28 ? p.substring(0, 28) + '...' : p}
              </button>
            ))}
          </div>

          {/* Message Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="p-3 bg-slate-900 border-t border-slate-800 flex items-center gap-2 shrink-0"
          >
            <input
              type="text"
              placeholder="Type message in English or Hindi..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="flex-1 bg-slate-950 border border-slate-800 rounded-full px-4 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
            />
            <button
              type="submit"
              disabled={loading || !inputText.trim()}
              className="w-9 h-9 rounded-full bg-emerald-600 hover:bg-emerald-500 text-white flex items-center justify-center transition-all disabled:opacity-40 shrink-0"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
