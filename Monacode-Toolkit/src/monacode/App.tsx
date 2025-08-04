// src/monacode/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';

import About from '@monacode/components/About';
import PasswordProtector from '@monacode/components/PasswordProtector';
import MainScreen from '@monacode/components/MainScreen';

import monacodeLogo from './assets/monacode-logo.png';

const styles: Record<string, React.CSSProperties> = {
    app: { display: 'flex', flexDirection: 'column', height: '100vh' },
    navbar: {
        display: 'flex',
        alignItems: 'center',
        background: '#282c34',
        padding: '0.5rem 1rem',
    },
    logo: { height: 40, marginRight: 16 },
    navList: {
        listStyle: 'none',
        display: 'flex',
        gap: 16,
        margin: 0,
        padding: 0,
    },
    link: { color: '#61dafb', textDecoration: 'none', fontSize: '1rem' },
    main: { flex: 1, position: 'relative' },
};

const App: React.FC = () => (
    <Router>
    <div style={styles.app}>
    <nav style={styles.navbar}>
    <img src={monacodeLogo} alt="Monacode Toolkit Logo" style={styles.logo} />
    <ul style={styles.navList}>
    <li><Link to="/app" style={styles.link}>Home</Link></li>
    <li><Link to="/about" style={styles.link}>About</Link></li>
    </ul>
    </nav>

    <main style={styles.main}>
    <Routes>
    <Route path="/" element={<Navigate to="/app" replace />} />
    <Route path="/app" element={<MainScreen />} />
    <Route path="/unlock" element={<PasswordProtector />} />
    <Route path="/about" element={<About />} />
    </Routes>
    </main>
    </div>
    </Router>
);

export default App;
