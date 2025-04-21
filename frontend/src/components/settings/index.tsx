'use client';
import Style from './settings.module.scss';
import Line from '@/components/line';

export default function Settings() {
  /*const { theme, setTheme } = useTheme();

  const optionsTheme = [
    {
      element: 'Светлая тема',
      value: 'light' as ThemeMode,
    },
    {
      element: 'Тёмная тема',
      value: 'dark' as ThemeMode,
    },
    {
      element: 'Тема системы (браузера)',
      value: 'system' as ThemeMode,
    },
  ];*/

  return (
    <>
      <Line />
      <h4 className={Style.HeadingSetting}>Настроек нету</h4>
    </>
  );
}

// <SegmentedField value={theme} setValue={setTheme} options={optionsTheme} />
