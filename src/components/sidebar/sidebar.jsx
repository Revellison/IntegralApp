import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faHome, 
  faFolder, 
  faTasks, 
  faCalendar, 
  faCog,
  faSun,
  faMoon
} from '@fortawesome/free-solid-svg-icons';
import './sidebar.css';

const Sidebar = () => {
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const menuItems = [
    { id: 1, icon: faHome },
    { id: 2, icon: faFolder },
    { id: 3, icon: faTasks },
    { id: 4, icon: faCalendar },
    { id: 5, icon: faCog },
  ];

  return (
    <div className="sidebar">
      <ul className="sidebar-menu">
        {menuItems.map((item) => (
          <li key={item.id} className="menu-item">
            <FontAwesomeIcon icon={item.icon} />
          </li>
        ))}
      </ul>
      <div className="theme-toggle" onClick={toggleTheme}>
        <FontAwesomeIcon icon={theme === 'dark' ? faSun : faMoon} />
      </div>
    </div>
  );
};

export default Sidebar;
