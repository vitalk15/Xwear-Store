import { Link } from 'react-router-dom'
import { getInternalPath } from '@/shared/utils/url'

// определяет как обрабатывать ссылки, которые приходят от бэкенда
const SmartLink = ({ to, children, className, ...props }) => {
	const internalPath = getInternalPath(to)

	// Если это внутренняя ссылка приложения — используем React Router (без перезагрузки)
	if (internalPath) {
		return (
			<Link to={internalPath} className={className} {...props}>
				{children}
			</Link>
		)
	}

	// Если это внешняя ссылка (или пустая) — рендерим обычный <a>
	return (
		<a
			href={to}
			className={className}
			target="_blank"
			rel="noopener noreferrer"
			{...props}
		>
			{children}
		</a>
	)
}

export default SmartLink
