import PageTitle from '@/components/common/PageTitle'

const HomePage = () => {
	return (
		<div
			style={{
				padding: '120px 40px',
				minHeight: '200vh',
				background: '#f9f9fb',
				color: '#121214',
			}}
		>
			<PageTitle title="Главная" />
			<h1 style={{ fontSize: '32px', marginBottom: '16px' }}>Главная страница</h1>
			<p style={{ color: '#8c8f96' }}>
				Покрутите страницу вниз, чтобы проверить, как плавно скрывается хедер.
			</p>
		</div>
	)
}

export default HomePage
