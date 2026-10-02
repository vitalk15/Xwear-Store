import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { SilentFallback } from '@/components/common/ErrorBoundary/SilentFallback'
import { handleCriticalError } from '@/shared/utils/errorHandler'
import ProfileContent from './ProfileContent'
import ProfileSkeleton from './ProfileSkeleton'
import PageTitle from '@/components/common/PageTitle'
import styles from './ProfilePage.module.scss'

const ProfilePage = () => {
	return (
		<>
			<PageTitle title="Личный кабинет" />

			<div className={`container ${styles.pageWrapper}`}>
				<ErrorBoundary fallback={<SilentFallback />} onError={handleCriticalError}>
					<Suspense fallback={<ProfileSkeleton />}>
						<ProfileContent />
					</Suspense>
				</ErrorBoundary>
			</div>
		</>
	)
}

export default ProfilePage
