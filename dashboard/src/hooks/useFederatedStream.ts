import { useEffect, useState } from 'react';
import type { ScopedSignal } from '../types/federation';

export function useFederatedStream<TPayload>(url: string, enabled = true) {
  const [messages, setMessages] = useState<Array<ScopedSignal<TPayload>>>([]);
  const [status, setStatus] = useState<'idle' | 'connecting' | 'open' | 'closed' | 'error'>('idle');

  useEffect(() => {
    if (!enabled) return;
    setStatus('connecting');
    const socket = new WebSocket(url);
    socket.onopen = () => setStatus('open');
    socket.onclose = () => setStatus('closed');
    socket.onerror = () => setStatus('error');
    socket.onmessage = (event) => {
      const parsed = JSON.parse(event.data) as ScopedSignal<TPayload>;
      setMessages((current) => [...current.slice(-100), parsed]);
    };
    return () => socket.close();
  }, [url, enabled]);

  return { messages, status };
}
