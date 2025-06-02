import React, { useState, useEffect, useRef } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faHome, 
  faPaintbrush,
  faCalculator,
  faLaptopCode,
  faBook,
  faCog,
  faSun,
  faMoon,
  faEllipsisV,
  faExternalLinkAlt,
  faStar,
  faHistory,
  faBookmark,
} from '@fortawesome/free-solid-svg-icons';
import './sidebar.css';

const Sidebar = () => {
  const [theme, setTheme] = useState('dark');
  const [activeDropdown, setActiveDropdown] = useState(null);
  const [activeSubmenu, setActiveSubmenu] = useState(null);
  const timeoutRef = useRef(null);
  const submenuTimeoutRef = useRef(null);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const handleMouseEnter = (id) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setActiveDropdown(id);
  };

  const handleMouseLeave = () => {
    timeoutRef.current = setTimeout(() => {
      setActiveDropdown(null);
    }, 300);
  };

  const handleSubmenuEnter = (id) => {
    if (submenuTimeoutRef.current) {
      clearTimeout(submenuTimeoutRef.current);
    }
    setActiveSubmenu(id);
  };

  const handleSubmenuLeave = () => {
    submenuTimeoutRef.current = setTimeout(() => {
      setActiveSubmenu(null);
    }, 300);
  };

  const topMenuItems = [
    { id: 'home', icon: faHome, label: 'Главная' },
    { id: 'draw', icon: faPaintbrush, label: 'Рисовалка' },
  ];

  const subjectMenuItems = [
    { 
      id: 3, 
      icon: faCalculator, 
      label: 'Математика',
      dropdown: [
        { id: 'math1', label: 'Алгебра' },
        { id: 'math2', label: 'Геометрия' },
        { id: 'math3', label: 'Тригонометрия' }
      ]
    },
    { 
      id: 4, 
      icon: faLaptopCode, 
      label: 'Информатика',
      dropdown: [
        { id: 'info1', label: 'Программирование' },
        { id: 'info2', label: 'Алгоритмы' },
        { id: 'info3', label: 'Базы данных' }
      ]
    },
    { 
      id: 5, 
      icon: faBook, 
      label: 'Русский язык',
      dropdown: [
        { id: 'rus1', label: 'Грамматика' },
        { id: 'rus2', label: 'Орфография' },
        { id: 'rus3', label: 'Пунктуация' }
      ]
    },
  ];

  const bottomMenuItems = [
    { id: 'settings', icon: faCog, label: 'Настройки' },
  ];

  const submenuItems = [
    { icon: faExternalLinkAlt, label: 'Открыть в новом окне' },
    { icon: faStar, label: 'Добавить в избранное' },
    { icon: faHistory, label: 'История' },
    { icon: faBookmark, label: 'Закладки' },
  ];

  const renderSimpleMenuItem = (item) => (
    <li 
      key={item.id} 
      className="menu-item"
      title={item.label}
    >
      <FontAwesomeIcon icon={item.icon} />
    </li>
  );

  const renderDropdownMenuItem = (item) => (
    <li 
      key={item.id} 
      className="menu-item"
      title={item.label}
      onMouseEnter={() => handleMouseEnter(item.id)}
      onMouseLeave={handleMouseLeave}
    >
      <FontAwesomeIcon icon={item.icon} />
      <div className={`dropdown-menu ${activeDropdown === item.id ? 'show' : ''}`}>
        {item.dropdown.map((subItem) => (
          <div key={subItem.id} className="dropdown-item">
            <span>{subItem.label}</span>
            <div 
              className="submenu-trigger"
              onMouseEnter={() => handleSubmenuEnter(subItem.id)}
              onMouseLeave={handleSubmenuLeave}
            >
              <FontAwesomeIcon icon={faEllipsisV} />
              <div className={`submenu ${activeSubmenu === subItem.id ? 'show' : ''}`}>
                {submenuItems.map((submenuItem, index) => (
                  <div key={index} className="submenu-item">
                    <FontAwesomeIcon icon={submenuItem.icon} />
                    <span>{submenuItem.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </li>
  );

  return (
    <div className="sidebar">
      <div className="sidebar-top">
        <ul className="sidebar-menu">
          {topMenuItems.map(renderSimpleMenuItem)}
        </ul>
      </div>

      <div className="sidebar-middle">
        <ul className="sidebar-menu">
          {subjectMenuItems.map(renderDropdownMenuItem)}
        </ul>
      </div>

      <div className="sidebar-bottom">
        <ul className="sidebar-menu">
          {bottomMenuItems.map(renderSimpleMenuItem)}
        </ul>
        <div className="theme-toggle" onClick={toggleTheme} title="Сменить тему">
          <FontAwesomeIcon icon={theme === 'dark' ? faSun : faMoon} />
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
