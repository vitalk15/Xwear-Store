import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { SilentFallback } from '@/components/common/ErrorBoundary/SilentFallback'
import { handleCriticalError } from '@/shared/utils/errorHandler'
import PageTitle from '@/components/common/PageTitle'
import ContactsContent from './ContactsContent'
import ContactsSkeleton from './ContactsSkeleton'
import styles from './ContactsPage.module.scss'

const ContactsPage = () => {
	return (
		<>
			<PageTitle title="Контакты" />

			<div className={`container ${styles.pageWrapper}`}>
				<ErrorBoundary fallback={<SilentFallback />} onError={handleCriticalError}>
					<Suspense fallback={<ContactsSkeleton />}>
						<ContactsContent />
					</Suspense>
				</ErrorBoundary>
			</div>
		</>
	)
}

export default ContactsPage
