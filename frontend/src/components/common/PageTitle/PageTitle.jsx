const PageTitle = ({ title }) => {
	const appName = import.meta.env.VITE_APP_TITLE || 'XWear'

	return <title>{`${appName} | ${title}`}</title>
}

export default PageTitle
