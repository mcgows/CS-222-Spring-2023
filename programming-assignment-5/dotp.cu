
#include "cuda_runtime.h"
#include <stdio.h>
#include <cmath>

__global__ void dotp(float* u, float* v, float* partialSum);

const int N = 256 * 256 * 256;
const int threadsPerBlock = 256;
const int numBlocks = (N + threadsPerBlock - 1) / threadsPerBlock;

int getDeviceInfo() {
    cudaDeviceProp prop;

    int count;
    cudaGetDeviceCount(&count);
    printf("there are %d device(s)\n", count);
    for (int i = 0; i < count; ++i) {
        cudaGetDeviceProperties(&prop, i);
        printf("name is %s\n", prop.name);
        printf("major.minor is %d.%d\n", prop.major, prop.minor);
        printf("multiProcessorCount is %d\n", prop.multiProcessorCount);
        printf("warpSize is %d\n", prop.warpSize);
        printf("maxThreadsPerBlock is %d\n", prop.maxThreadsPerBlock);
        printf("maxThreadsDim is (%d, %d, %d)\n", prop.maxThreadsDim[0],
            prop.maxThreadsDim[1], prop.maxThreadsDim[2]);
        printf("maxGridSize is (%d, %d, %d)\n", prop.maxGridSize[0],
            prop.maxGridSize[1], prop.maxGridSize[2]);
        if (prop.deviceOverlap)
            printf("device overlap is enabled\n");
        else
            printf("device overlap is NOT enabled\n");
    }

    return 0;
}

float dotp_cpu(float* u, float* v) {
	float temp = 0.0;
	for (int i = 0; i < N; i++) {
		temp += u[i] * v[i];
	}
	return temp;
}

__global__
void dotp(float* u, float* v, float* partialSum) {
	__shared__ float cache[threadsPerBlock];
	int tid = threadIdx.x + blockIdx.x * blockDim.x;
	int cacheIndex = threadIdx.x;
	int stride = blockDim.x * gridDim.x;
	float temp = 0.0;

	while (tid < N) {
		temp += u[tid] * v[tid];
		tid += stride;
	}
	// set the cache values
	cache[cacheIndex] = temp;

	// synchronize threads in this block
	__syncthreads();

	// for reductions, threadsPerBlock must be a power of 2
	// because of the following code
	int i = blockDim.x / 2;
	while (i > 0) {
		if (cacheIndex < i)
			cache[cacheIndex] += cache[cacheIndex + i];
		__syncthreads();
		i /= 2;
	}

	if (cacheIndex == 0)
		partialSum[blockIdx.x] = cache[0];
}

int main() {
	float *U, *V, w, * partialSum;
	float *dev_U, *dev_V, *dev_Z;

	cudaEvent_t startNoMem, startMem, stop, cpuStart, cpuStop;
	cudaEventCreate(&startNoMem);
	cudaEventCreate(&startMem);
	cudaEventCreate(&stop);
	cudaEventCreate(&cpuStart);
	cudaEventCreate(&cpuStop);

	// allocate memory on the cpu side
	U = (float *) malloc (N * sizeof(float));
	V = (float *) malloc (N * sizeof(float));
	partialSum = (float *) malloc (numBlocks * sizeof(float));

	// fill in the host mempory with data
	// NOTE : this methodology came from stack overflow as I needed to convert from drand48() to windows specific commands.
	srand(time(NULL));
	for (int i = 0; i < N; i++) {
		U[i] = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);
		V[i] = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);
	}

	cudaEventRecord(startMem, 0);
	// allocate the memory on the gpu
	cudaMalloc((void**)&dev_U, N * sizeof(float));
	cudaMalloc((void**)&dev_V, N * sizeof(float));
	cudaMalloc((void**)&dev_Z, numBlocks * sizeof(float));

	// copy the arrays 'u' and 'v' to the gpu
	cudaMemcpy(dev_U, U, N * sizeof(float), cudaMemcpyHostToDevice);
	cudaMemcpy(dev_V, V, N * sizeof(float), cudaMemcpyHostToDevice);


	cudaEventRecord(startNoMem, 0);
	dotp <<<numBlocks, threadsPerBlock>>> (dev_U, dev_V, dev_Z);
	cudaDeviceSynchronize(); // wait for GPU threads to complete; again, not necessary but good pratice
	cudaEventRecord(stop, 0);

	// copy the array 'dev_Z' back from the gpu to the cpu into partialSum
	cudaMemcpy(partialSum, dev_Z, numBlocks * sizeof(float), cudaMemcpyDeviceToHost);


	// finish up on the cpu side
	w = 0;
	for (int i = 0; i < numBlocks; i++) {
		w += partialSum[i];
	}


	cudaEventRecord(cpuStart, 0);
	float cpuDotpSum = dotp_cpu(U, V);
	cudaEventRecord(cpuStop, 0);

	float elapsedTimeNoMem, elapsedTimeMem, elapsedTimeCpu;
	cudaEventElapsedTime(&elapsedTimeMem, startMem, stop);
	cudaEventElapsedTime(&elapsedTimeNoMem, startNoMem, stop);
	cudaEventElapsedTime(&elapsedTimeCpu, cpuStart, cpuStop);


	printf("Relative Error [ GPU vs. CPU] rounded to ten thousandths of a percent : %.3g%%\n", (abs(w) - abs(cpuDotpSum)) / abs(w));
	printf("GPU Execution time [ Memory Operations Counted ] : %f ms\n", elapsedTimeMem);
	printf("GPU Execution time [ No Memory Operations ] : %f ms\n", elapsedTimeNoMem);
	printf("CPU Execution time : %g ms\n", elapsedTimeCpu);


	// free memory on the gpu side
	cudaFree(dev_U);
	cudaFree(dev_V);
	cudaFree(dev_Z);

	// free memory on the cpu side
	free(U);
	free(V);
	free(partialSum);

    return 0;
}