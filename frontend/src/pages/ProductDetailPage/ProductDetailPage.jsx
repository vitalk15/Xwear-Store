import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { SilentFallback } from '@/components/common/ErrorBoundary/SilentFallback'
import { useProductDetail } from '@/features/catalog/hooks/useProductDetail'
import { handleCriticalError } from '@/shared/utils/errorHandler'
import PageTitle from '@/components/common/PageTitle'
import ProductDetailContent from './ProductDetailContent'
import ProductDetailSkeleton from './ ProductDetailSkeleton'
import styles from './ProductDetailPage.module.scss'

const ProductDetailPage = ({ productId }) => {
	const { data: product } = useProductDetail(productId)

	return (
		<>
			<PageTitle title={product.naming.full_title} />

			<div className={`container ${styles.pageWrapper}`}>
				<ErrorBoundary fallback={<SilentFallback />} onError={handleCriticalError}>
					<Suspense fallback={<ProductDetailSkeleton />}>
						<ProductDetailContent product={product} />
					</Suspense>
				</ErrorBoundary>
			</div>
		</>
	)
}

export default ProductDetailPage
