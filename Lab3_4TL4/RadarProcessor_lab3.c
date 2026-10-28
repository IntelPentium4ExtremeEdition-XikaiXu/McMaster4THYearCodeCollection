// Template for C6713 DSK and AIC23 codec
#define CHIP_6713

#include "dsk6713.h"
#include "dsk6713_aic23.h" //
#include <stdio.h>
#include <math.h>

#include "data_trans.h"
#include "data_rec.h"
//#include "data_dechirp.h"

typedef struct {float real,imag;} COMPLEX;
COMPLEX range_signal[500];//[NUM_SAMPLES_PER_CHIRP];

DSK6713_AIC23_CodecHandle hCodec;							// Codec handle
DSK6713_AIC23_Config config = DSK6713_AIC23_DEFAULTCONFIG;  // Codec configuration with default settings

///////////////////////////////////
int interrupt_count = 0;
double MAX_SIGNAL_VALUE = 0;

void initialize();
short convert_double_to_short_for_output(double max_value, double input_value);

void convolution(float* real_ref, float* imag_ref, float* real_rec, float* imag_rec, int num_samples, COMPLEX* output)
{
	int n;
	int k;
	for (n=0; n < num_samples; n++){
		output[n].real = 0;
		output[n].imag = 0;
		for (k=0; k < num_samples; k++){
			int ref_i = k-n;
			if (ref_i < 0){
				ref_i = num_samples - (n - k); // This is the loop conv, used for periodic, linear conv used for small piece
			}
			output[n].real += real_ref[ref_i]*real_rec[k] + imag_ref[ref_i]*imag_rec[k];
			output[n].imag += real_ref[ref_i]*imag_rec[k] - imag_ref[ref_i]*real_rec[k];
		}			
	}	
}

void save_results(COMPLEX* data, int N)
{
//	FILE *save = fopen("result.csv");
	int index;
//	fprintf(save,"header","real","imag","amp","num","index");
//	for(index = 0; index < N; ++index) {
//		fwrite(save, *data[index].real, *data[index].imag, sqrt(*data[index].real**2 + *data[index].imag**2), *data[index], index);
//	}
//
//	fclose("result.csv");

    FILE *save = fopen("result.csv", "w");
    printf("LOL");
    fprintf(save, "real,imag,amp,index\n");
    for (index = 0; index < N; ++index) {
        double real = data[index].real;
        double imag = data[index].imag;
        double amp = sqrt(real * real + imag * imag);
        fprintf(save, "%f,%f,%f,%d\n", real, imag, amp, index);
    }
    fclose(save);


}


void main()
{
	interrupt_count = 0; 
	
	initialize();
	
	convolution(sig_real, sig_img, rec_real, rec_img, NUM_SAMPLES_PER_CHIRP, range_signal);	
	
	save_results(range_signal, NUM_SAMPLES_PER_CHIRP);
	
	MAX_SIGNAL_VALUE = 0;       //for c_int11 to recalculate the max value
	while(1);					// main loop - do nothing but wait for interrupts
}

/** interrupt service routine */
interrupt void c_int11()		
{
	int num_gaps_to_insert = 50;
	double sig;	
	if (interrupt_count < NUM_SAMPLES){
		sig = sqrt(range_signal[interrupt_count].real*range_signal[interrupt_count].real + range_signal[interrupt_count].imag*range_signal[interrupt_count].imag);	
	}
	else if (interrupt_count < NUM_SAMPLES + num_gaps_to_insert){
		sig = -0.5*MAX_SIGNAL_VALUE;//0;
	}
	
	interrupt_count = interrupt_count+1;// freq based on the clock generator of the silicon
	if (interrupt_count >= NUM_SAMPLES + num_gaps_to_insert){
		interrupt_count = 0;
	}
	
	if (sig > MAX_SIGNAL_VALUE){
		MAX_SIGNAL_VALUE = sig;
	}		
		
	short sig_out = convert_double_to_short_for_output(MAX_SIGNAL_VALUE, sig);
	
	/* DO NOT MODIFY ANYTHING BELOW */	
	sig_out = -1*sig_out; //Board inverts the signal from the DAC.
	
	union {Uint32 stereo; short channel[2];} audio;	
	audio.channel[1] = sig_out;	// insert left channel
	audio.channel[0] = sig_out;	// insert right channel
	MCBSP_write(DSK6713_AIC23_DATAHANDLE, audio.stereo); // write stereo audio
}

/* DO NOT MODIFY ANYTHING BELOW */
void vectors();         // external function

short convert_double_to_short_for_output(double max_value, double input_value)
{	
	short MAX_POSITIVE_VALUE = 32700;//32767
	
	if (input_value > max_value)
		input_value = max_value;
	
	short result = (short)(MAX_POSITIVE_VALUE/max_value*input_value);
	
	return result;
}

void initialize()
{
	// initialize dsp
	DSK6713_init();		//call BSL to init DSK-EMIF,PLL)

	DSK6713_LED_init();

	// initialize AIC23 peripheral
	hCodec = DSK6713_AIC23_openCodec(0, &config);	//handle(pointer) to codec
	DSK6713_AIC23_setFreq(hCodec, DSK6713_AIC23_FREQ_8KHZ);//set sample rate
	// Configure buffered serial ports for 32 bit operation
	// This allows transfer of both right and left channels in one read/write
	MCBSP_FSETS(SPCR1, RINTM, FRM);
	MCBSP_FSETS(SPCR1, XINTM, FRM);
	MCBSP_FSETS(RCR1, RWDLEN1, 32BIT);
	MCBSP_FSETS(XCR1, XWDLEN1, 32BIT);
	MCBSP_start(DSK6713_AIC23_DATAHANDLE, MCBSP_XMIT_START | MCBSP_RCV_START |
			MCBSP_SRGR_START | MCBSP_SRGR_FRAMESYNC, 220);// re-start data channel

	// initialize interrupt
	Uint32 CODECEventId;
	IRQ_globalDisable();		// disable interrupts
	CODECEventId=MCBSP_getXmtEventId(DSK6713_AIC23_codecdatahandle);// McBSP1 Xmit
	IRQ_setVecs(vectors);    	// point to the IRQ vector table
	IRQ_map(CODECEventId,11);	// Maps an event to a physical interrupt
	IRQ_reset(CODECEventId); 	// reset codec INT 11
	IRQ_globalEnable();			// Globally enables interrupts
	IRQ_nmiEnable();			// Enables the non-maskable interrupts
	IRQ_enable(CODECEventId);	// enable CODEC eventXmit INT11
	MCBSP_write(DSK6713_AIC23_DATAHANDLE,0);// start interrupt by outputting a sample
}
