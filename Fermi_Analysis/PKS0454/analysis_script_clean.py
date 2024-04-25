import fermipy
import yaml
import argparse
from fermipy.gtanalysis import GTAnalysis


def main():

    ##### CONFIGURATION FILE #####
    usage = "usage: %(prog)s [config file]"
    description = "Run fermipy analysis"
    
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()

    config = yaml.safe_load(open(str(args.config))) #load funktioniert nicht

    gta = GTAnalysis(args.config)
    
    #### SETUP analysis ####
    gta.setup() 
    
    ## When using a xml-file as catalog, make sure to fix all sources before. (Otherwise their parameters are as default free)
    gta.free_sources(False)

    source_name = config["selection"]["target"]
            
    # OPTIMIZE
    ## ------------ ##
    for j in range(1):
    	print(f'-------\nOptimization {j}\n-------')
    	gta.optimize()
    
    gta.print_model()
    
    ## FIND NEW SOURCES
    ## -------------------- ##
    model = {'SpectrumType': 'PowerLaw', 'SpatialModel': 'PointSource'}
    srcs = gta.find_sources(model=model, sqrt_ts_threshold=5.,min_separation=0.3)  #sqrt_ts_threshold default: 5.0
    
    ## reoptimize the model including NEW SOURCES
    ## ----------------------------- ##
    if len(srcs['sources'])>0:
    	gta.setup()
    	for j in range(1):
    	    print(f'-------\nFind_Sources Optimization {j}\n-------')
    	    gta.optimize()
    
    # Overfitted with 11 runs!!    
    #for j in range(4):
    #	print(f'-------\nOptimization {j}\n-------')
    #	gta.optimize()

    ## Residual map and TSmap
    ## ------------- ##
    maps0 = gta.residmap('postfit', model=model, make_plots=True)
    tsmapNo = gta.tsmap(prefix='noExclude', make_plots=True)
    tsmap = gta.tsmap(prefix='Exclude', exclude=source_name, make_plots=True)
    
    
    ## Record best-fit results
    ## ------------------------- ##
    gta.write_roi("bestfit",make_plots=True)
    
        
    gta.print_model()
    
    print("*****************\nFINAL FIT VALUES\n*****************")
    gta.print_roi()
    print("Source: ",gta.roi.sources[0]["name"])
    print("TS: ",gta.roi.sources[0]["ts"])
    
    ## Compute gamma-ray spectrum
    ## -------------- ##
    sed = gta.sed(source_name, free_background=True, make_plots=True, cov_scale=None, loge_bins=gta.log_energies[::2])
    
    ## Compute gamma-ray lightcurve
    ## ------------ ##
    time = 1 # this is how many months
    binsize = time *28*86400.0 # get the bin length in seconds
    lc = gta.lightcurve(source_name, binsz=binsize, free_background=True, save_bin_data=True, free_params=['norm'], use_local_ltcube=True, use_scaled_srcmap=True, shape_ts_threshold=500000000.0, outdir = 'bin_%s_months'%(time), prefix=time)
    
    print('***************\nanalysis completed\n***************')
    
    return gta

if __name__ == "__main__":
    gta = main()
