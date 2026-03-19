import { createContext, useContext, useMemo, useState } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState(() => {
    const saved = localStorage.getItem('annabanai-auth');
    return saved ? JSON.parse(saved) : { token: '', user: null };
  });

  const updateAuth = (value) => {
    setAuth(value);
    localStorage.setItem('annabanai-auth', JSON.stringify(value));
  };

  const logout = () => {
    setAuth({ token: '', user: null });
    localStorage.removeItem('annabanai-auth');
  };

  const contextValue = useMemo(() => ({ auth, updateAuth, logout }), [auth]);

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
