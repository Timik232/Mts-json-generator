import { useEffect } from 'react';
import useLocalStorage from '@/hooks/useLocalStorage';

export type ThemeMode = 'light' | 'dark' | 'system';
type ActiveTheme = 'light' | 'dark';

const useTheme = () => {
  const [theme, setTheme] = useLocalStorage<ThemeMode>('theme', 'system');

  const getSystemTheme = (): ActiveTheme => {
    // Защита от выполнения на сервере
    if (typeof window === 'undefined') return 'light';
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  };

  const applyTheme = (newTheme: ThemeMode) => {
    // Защита от выполнения на сервере
    if (typeof document === 'undefined') return;

    let activeTheme: ActiveTheme;

    if (newTheme === 'system') {
      activeTheme = getSystemTheme();
    } else {
      activeTheme = newTheme;
    }

    if (activeTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  // Инициализация темы только на клиенте
  useEffect(() => {
    applyTheme(theme);
  }, []);

  // Обработчик изменений только на клиенте
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleSystemThemeChange = (e: MediaQueryListEvent) => {
      console.log(e);
      if (theme === 'system') {
        applyTheme('system');
      }
    };

    mediaQuery.addEventListener('change', handleSystemThemeChange);
    applyTheme(theme);

    return () => {
      mediaQuery.removeEventListener('change', handleSystemThemeChange);
    };
  }, [theme]);

  return {
    theme,
    setTheme,
    activeTheme: theme === 'system' ? getSystemTheme() : theme,
  };
};

export default useTheme;
