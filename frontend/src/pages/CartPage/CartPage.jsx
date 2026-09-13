import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { SilentFallback } from '@/components/common/ErrorBoundary/SilentFallback'
import { handleCriticalError } from '@/shared/utils/errorHandler'
import PageTitle from '@/components/common/PageTitle'
import CartContent from './CartContent'
import CartSkeleton from './CartSkeleton'
import styles from './CartPage.module.scss'

const CartPage = () => {
	return (
		<>
			<PageTitle title="Корзина" />

			<div className={`container ${styles.pageWrapper}`}>
				<ErrorBoundary fallback={<SilentFallback />} onError={handleCriticalError}>
					<Suspense fallback={<CartSkeleton />}>
						<CartContent />
					</Suspense>
				</ErrorBoundary>
			</div>
		</>
	)
}

export default CartPage
