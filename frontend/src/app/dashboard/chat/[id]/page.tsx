"use client";

import { useEffect, useState, useRef } from "react";
import { Send, Search, MoreVertical, ArrowLeft, BotMessageSquare } from "lucide-react";
import { toast } from "react-hot-toast";
import { api } from "@/lib/api";

export default function P2PChat({ params }: { params: { id: string } }) {
    const tenderId = params.id;
    const [messages, setMessages] = useState<any[]>([]);
    const [inputText, setInputText] = useState("");
    const [myId, setMyId] = useState<number>(0);
    const [partnerId, setPartnerId] = useState<number>(0); // Пока мы зашиваем хардкодом для тестов или берем из контекста
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (typeof window !== "undefined" && (window as any).Telegram?.WebApp?.initDataUnsafe?.user?.id) {
            setMyId((window as any).Telegram.WebApp.initDataUnsafe.user.id);
            // Для демо мы предполагаем, что partner_id передается в query или мы бьемся с 1 админом (0)
            setPartnerId(0); 
        } else {
            setMyId(123); // Desktop Mock 
            setPartnerId(456);
        }
    }, []);

    useEffect(() => {
        if (myId === 0) return;
        fetchHistory();
        
        // Polling (Раз в 5 секунд)
        const interval = setInterval(() => {
            fetchHistory();
        }, 5000);
        return () => clearInterval(interval);
    }, [myId, partnerId, tenderId]);

    const fetchHistory = async () => {
        try {
            const data = await api.get<{ ok: boolean; messages: any[] }>(`/chat/history?tender_id=${tenderId}&user1=${myId}&user2=${partnerId}`);
            if (data.ok) {
                setMessages(data.messages);
                scrollToBottom();
            }
        } catch {
            console.error("Failed to load history");
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputText.trim()) return;

        const tmpMsg = { id: Date.now(), sender_id: myId, receiver_id: partnerId, content: inputText, created_at: new Date().toISOString() };
        setMessages(prev => [...prev, tmpMsg]);
        setInputText("");
        scrollToBottom();

        try {
            await api.post("/chat/send", {
                tender_id: parseInt(tenderId),
                sender_id: myId,
                receiver_id: partnerId,
                content: tmpMsg.content
            });
        } catch {
            toast.error("Ошибка при отправке");
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-80px)] bg-[#0A0A0B]">
            {/* Header */}
            <header className="flex items-center justify-between p-4 bg-[#121214] border-b border-white/5 sticky top-0 z-10">
                <div className="flex items-center gap-3">
                    <button onClick={() => window.history.back()} className="p-2 text-gray-400 hover:text-white rounded-full bg-white/5 transition-all">
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div>
                        <h1 className="text-white font-bold text-lg leading-tight flex items-center gap-2">
                            Сделка #{tenderId}
                        </h1>
                        <p className="text-xs text-khokhloma-gold">Безопасная переписка P2P</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button className="text-gray-400 p-2 hover:bg-white/5 rounded-full"><Search className="w-5 h-5" /></button>
                    <button className="text-gray-400 p-2 hover:bg-white/5 rounded-full"><MoreVertical className="w-5 h-5" /></button>
                </div>
            </header>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 fancy-scrollbar relative bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]">
                <div className="text-center my-4">
                    <span className="text-[10px] uppercase font-bold text-gray-500 bg-[#121214] border border-white/5 px-3 py-1 rounded-full">
                        Чат привязан к Тендеру
                    </span>
                </div>

                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 space-y-4">
                        <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center">
                            <BotMessageSquare className="w-8 h-8 text-white/50" />
                        </div>
                        <p className="max-w-[250px] text-sm">Здесь будет ваша переписка с партнером. Обсуждайте детали безопасно.</p>
                    </div>
                ) : (
                    messages.map((m, idx) => {
                        const isMe = m.sender_id === myId;
                        return (
                            <div key={m.id || idx} className={`flex ${isMe ? "justify-end" : "justify-start"} animate-in slide-in-from-bottom-2`}>
                                <div className={`max-w-[80%] rounded-2xl p-3 ${isMe ? "bg-khokhloma-gold text-black rounded-tr-none shadow-[0_0_15px_rgba(255,215,0,0.15)]" : "bg-[#18181B] border border-white/10 text-white rounded-tl-none"}`}>
                                    <p className="text-sm break-words whitespace-pre-wrap">{m.content}</p>
                                    <div className={`text-[10px] mt-1 text-right ${isMe ? "text-black/60" : "text-gray-500"}`}>
                                        {new Date(m.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                    </div>
                                </div>
                            </div>
                        );
                    })
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <form onSubmit={handleSend} className="p-4 bg-[#121214] border-t border-white/5">
                <div className="flex items-end gap-2 bg-[#1A1A1D] border border-white/10 rounded-2xl p-1 pr-2 shadow-inner focus-within:border-khokhloma-gold/50 transition-colors">
                    <textarea 
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        placeholder="Сообщение..."
                        className="flex-1 bg-transparent text-white placeholder-gray-500 p-3 outline-none resize-none max-h-32 min-h-[44px] text-sm custom-scrollbar"
                        rows={1}
                        onKeyDown={(e) => {
                            if (e.key === "Enter" && !e.shiftKey) {
                                e.preventDefault();
                                handleSend(e);
                            }
                        }}
                    />
                    <button 
                        type="submit" 
                        disabled={!inputText.trim()}
                        className="bg-khokhloma-gold hover:bg-yellow-600 disabled:bg-white/10 disabled:text-gray-500 text-black p-3 mb-1 rounded-xl transition-all shadow-md"
                    >
                        <Send className="w-5 h-5 -ml-0.5" />
                    </button>
                </div>
                <div className="text-center mt-2">
                    <p className="text-[9px] text-gray-600 uppercase tracking-widest">Gorizont Secure Chat v2.0</p>
                </div>
            </form>
        </div>
    );
}
