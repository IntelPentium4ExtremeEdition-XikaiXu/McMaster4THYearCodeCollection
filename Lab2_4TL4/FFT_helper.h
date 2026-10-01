#include "math.h"
#include <stdio.h>

#define PTS 512		//# of points for FFT, should be 2^n
#define PI 3.14159265358979

#ifndef USE_FFT_LIB
typedef struct {float real,imag;} COMPLEX;
COMPLEX w_fft[PTS];			//twiddle constants stored in w
COMPLEX data_fft[PTS];		//primary working buffer

//#pragma DATA_SECTION(w_fft, ".extRAM");

/* generate complex twiddle for fft calculation                      */
void prepare_w_fft(COMPLEX* w, int N){
/*        w : FFT coefficients (dimension: N)                (output)         */
/*        n : FFT size which is a power of 2 and > 4         (input)          */

	int i = 0;
	for (i = 0 ; i<N ; i++)			 // set up twiddle constants in w
	{
		w[i].real = cos(2*PI*i/(2*N)); // Real component of twiddle constants
		w[i].imag =-sin(2*PI*i/(2*N)); // Imaginary component of twiddle constants
	}
}

/* Find the FFT of given sequence and overwrite the input sequence wih the output */
void FFT(COMPLEX *Y, COMPLEX* w, int N)	{
/*       Y: input and output sequences (dimension: N),         (input/output)        */
/*       w: complex twiddle (dimension: N),                    (input)        */
/*       N: number of points which is a power of 2 and > 4     (input)              */


	COMPLEX temp1,temp2;		// temporary storage variables
	int i, j, k;				// loop counter variables
	int upper_leg, lower_leg;	// index of upper/lower butterfly leg
	int leg_diff;				// difference between upper/lower leg
	int num_stages = 0;			// number of FFT stages (iterations)
	int index, step;			// index/step through twiddle constant
	i = 1;						// log(base2) of N points= # of stages

	if (log2(N) - round(log2(N)) != 0)
	{
		printf("Error! N for FFT should be 2^x.");
	}

	do
	{
		num_stages +=1;
		i = i*2;
	}
	while (i!=N);
	leg_diff = N/2;				//difference between upper&lower legs
	step = 2;					//step between values in twiddle.h
	for (i = 0;i < num_stages; i++)	//for N-point FFT
	{
		index = 0;
		for (j = 0; j < leg_diff; j++)
		{
			for (upper_leg = j; upper_leg < N; upper_leg += (2*leg_diff))
			{
				lower_leg = upper_leg+leg_diff;
				temp1.real = (Y[upper_leg]).real + (Y[lower_leg]).real;
				temp1.imag = (Y[upper_leg]).imag + (Y[lower_leg]).imag;
				temp2.real = (Y[upper_leg]).real - (Y[lower_leg]).real;
				temp2.imag = (Y[upper_leg]).imag - (Y[lower_leg]).imag;
				(Y[lower_leg]).real = temp2.real*(w[index]).real
									-temp2.imag*(w[index]).imag;
				(Y[lower_leg]).imag = temp2.real*(w[index]).imag
									+temp2.imag*(w[index]).real;
				(Y[upper_leg]).real = temp1.real;
				(Y[upper_leg]).imag = temp1.imag;
			}
			index += step;
		}
		leg_diff = leg_diff/2;
		step *= 2;
	}
	j = 0;
	for (i = 1; i < (N-1); i++)	//bit reversal for re-sequencing data
	{
		k = N/2;
		while (k <= j)
		{
			j = j - k;
			k = k/2;
		}
		j = j + k;
		if (i<j)
		{
			temp1.real = (Y[j]).real;
			temp1.imag = (Y[j]).imag;
			(Y[j]).real = (Y[i]).real;
			(Y[j]).imag = (Y[i]).imag;
			(Y[i]).real = temp1.real;
			(Y[i]).imag = temp1.imag;
		}
	}
	return;
}

#else
	
#include <DSPF_dp_cfftr2.h>

double data_fft_lib[PTS*2];		//primary working buffer
double w_fft_lib[PTS*2];

/* generate real and imaginary twiddle for fft calculation                      */
void prepare_w_fft_lib(double* w, int n){
/*        w : FFT coefficients (dimension: 2*n)                (output)         */
/*            w has n complex numbers (2*n double values).                      */
/*            The real and imaginary values are interleaved in memory.          */
/*        n : FFT size which is a power of 2 and > 4  (input)                   */

    int i, j=1;                    
	double pi = 4.0*atan(1.0);     
	double e = pi*2.0/n;           
	for(j=1; j < n; j <<= 1)       
	{                              
		for(i=0; i < ( n>>1 ); i += j) 
	    {                           
			*w++   = cos(i*e);          
			*w++   = -sin(i*e);         
		}                           
	} 
}

/*      This routine bit reverses the floating point array x which          */
/*      is considered to be an array of complex numbers with the even       */
/*      numbered elements being the real parts of the complex numbers       */
/*      while the odd numbered elements being the imaginary parts of the    */
/*      complex numbers.                                                    */
void bit_rev_2(double* x, int n){
/*      x              : Array to be bit-reversed.                          */
/*      n              : Number of complex array elements to bit-reverse.   */

  int i, j, k;
  double rtemp, itemp;

  j = 0;
  for(i=1; i < (n-1); i++)
  {
    k = n >> 1;
     while(k <= j)
     {
        j -= k;
        k >>= 1;
     }
     j += k;
     if(i < j)
     {
        rtemp    = x[j*2];
        x[j*2]   = x[i*2];
        x[i*2]   = rtemp;
        itemp    = x[j*2+1];
        x[j*2+1] = x[i*2+1];
        x[i*2+1] = itemp;
     }
  }
}
	
#endif
