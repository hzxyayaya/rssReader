/** @type {import('tailwindcss').Config} */
// TailwindCSS 配置 - 极简主题
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            // 自定义字体
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
                serif: ['Georgia', 'Cambria', 'serif'],
            },
            // 自定义颜色
            colors: {
                // 浅色主题
                light: {
                    bg: '#fafafa',
                    surface: '#ffffff',
                    text: '#1a1a1a',
                    muted: '#6b7280',
                    border: '#e5e7eb',
                    accent: '#3b82f6',
                },
                // 深色主题
                dark: {
                    bg: '#0f0f0f',
                    surface: '#1a1a1a',
                    text: '#f5f5f5',
                    muted: '#9ca3af',
                    border: '#2d2d2d',
                    accent: '#60a5fa',
                },
                // 护眼主题 (Sepia)
                sepia: {
                    bg: '#f4ecd8',
                    surface: '#faf6eb',
                    text: '#3d3929',
                    muted: '#6b6352',
                    border: '#d9d0b8',
                    accent: '#8b7355',
                },
            },
            // 阅读优化的行高
            lineHeight: {
                'reading': '1.8',
                'relaxed-reading': '2',
            },
            // 阅读区域最大宽度
            maxWidth: {
                'reading': '65ch',
            },
        },
    },
    plugins: [],
}
