"""

Python code to open and interpret OPUS file

A.G.Geddes

24/3/17

CURRENTLY SETUP UP TO RUN FROM WITHIN PYTHON, FILENAME HARDCODED, ARGUMENTS
AND CLEVER HELP PROMPTS DISABLED

How to run;

python handler.py filename arguments

enter python handler.py -h or --help for more information,

comment out references to arguments to run within python environment, uncomment
filename

Edit 18/05/17 - AG
Now includes all the spectra and interferogram data if available in the opus
file, as well as calculating an appropriate x-axis for each

"""



from numpy import *
import struct
import sys
import argparse
from matplotlib.pyplot import *
"""Setting up the arguments and help information"""



def read_string(block_string_input):
    """Reads a string until a space is reached from a binary string"""
    end_of_string=block_string_input[5:].index(' ')
    string_output=block_string_input[5:5+end_of_string]
    return string_output
    

def read_string_fix(block_string_input,length):
    """Reads date string which has a fixed length as there is no space afterwards"""

    #end_of_string=block_string_input[5:].index(' ')
    string_output=block_string_input[5:5+length]
    return string_output
    



    
class opus_header(object):
    """OPUS header class, I've put all the header info in to a class, for some
    reason, probably something silly on my part, I couldnt do this all in one 
    unpack call as it didnt like mixing my integers with double precision"""  
    def __init__(self,data):
        self.data=data
        self.output=dict(magic_number=self.magic_number(),prg_version_number=self.prg_version_number(),pointer=self.pointer(),max_size=self.max_size(),current_size=self.current_size())
    def magic_number(self):
        return (struct.unpack('i',data[0:4])[0])
    def prg_version_number(self):
        return (struct.unpack('d',data[4:12])[0])
    def pointer(self):
        return (struct.unpack('i',data[12:16])[0])
    def max_size(self):
        return (struct.unpack('i',data[16:20])[0])
    def current_size(self):
        return (struct.unpack('i',data[20:24])[0])
    
    



     
class interferogram_parameters(object):
    """Parameters from the interferogram block, at the moment ive only taken
    the date and time, I can add more as needed"""
    def find_parameter(self,name):
        block_string=struct.unpack(str(self.length_b)+'s',self.data[self.pointer:self.pointer+self.length_b])[0]

        parameter_index=block_string.index(str(name))
        parameter_index=parameter_index+len(name)
        return parameter_index,block_string
    def __init__(self,data,pointer,length):
        self.data=data
        self.pointer=pointer
        self.length=length
        self.length_b=4*length
        self.output=dict(time=self.time(),date=self.date(),x_array=self.x_array()) #Can ignore
    def time(self):
        """Measurement Time"""
        parameter_index,block_string=self.find_parameter('TIM')
        time=read_string_fix(block_string[parameter_index:],8)
        return time
    def date(self):
        """Date"""
        parameter_index,block_string=self.find_parameter('DAT')
        date=read_string_fix(block_string[parameter_index:],10)
        return date
    def npts(self):
        """Number of points in measurement"""
        parameter_index,block_string=self.find_parameter('NPT')
        block_float=struct.unpack('i',self.data[self.pointer+5+parameter_index:self.pointer+parameter_index+5+4])[0]
        return block_float
    def xmin(self):
        """Minimum X Value"""
        parameter_index,block_string=self.find_parameter('FXV')
        block_float=struct.unpack('d',self.data[self.pointer+5+parameter_index:self.pointer+parameter_index+5+8])[0]
        return block_float
    def xmax(self):
        """Maximum X Value"""
        parameter_index,block_string=self.find_parameter('LXV')
        block_float=struct.unpack('d',self.data[self.pointer+5+parameter_index:self.pointer+parameter_index+5+8])[0]
        return block_float
    def x_array(self):
        """X Array constructed from xmin, xmax and npts"""
        x_array=linspace(self.xmin(),self.xmax(),self.npts())
        return x_array
        
        
class instrument_parameters(object):
    """Parameters from the instruemnt block, at the moment ive only taken 
    duration of the measurement, more are available"""


    def find_parameter(self,name):
        block_string=struct.unpack(str(self.length_b)+'s',self.data[self.pointer:self.pointer+self.length_b])[0]
        parameter_index=block_string.index(str(name))
        parameter_index=parameter_index+len(name)
        return parameter_index,block_string
    def __init__(self,data,pointer,length):
        self.data=data
        self.pointer=pointer
        self.length=length
        self.length_b=4*length
        self.output=dict(duration=self.duration()) #Can ignore

    def duration(self):
        parameter_index,block_string=self.find_parameter('DUR')
        block_float=struct.unpack('d',self.data[self.pointer+parameter_index+5:self.pointer+parameter_index+8+5])[0]
        return block_float
        
        
class spectra_parameters(object):
    """Parameters from the instruemnt block"""


    def find_parameter(self,name):
        block_string=struct.unpack(str(self.length_b)+'s',self.data[self.pointer:self.pointer+self.length_b])[0]
        parameter_index=block_string.index(str(name))
        parameter_index=parameter_index+len(name)
        return parameter_index,block_string
    def __init__(self,data,pointer,length):
        self.data=data
        self.pointer=pointer
        self.length=length
        self.length_b=4*length
        
        self.output=dict(time=self.time(),date=self.date(),x_array=self.x_array()) #Can ignore
        
    def time(self):
        """Measurement Time"""
        parameter_index,block_string=self.find_parameter('TIM')
        time=read_string_fix(block_string[parameter_index:],8)
        return time
    def date(self):
        """Measurement Date"""
        parameter_index,block_string=self.find_parameter('DAT')
        date=read_string_fix(block_string[parameter_index:],10)
        return date
    def npts(self):
        """Number of points in measurement"""
        parameter_index,block_string=self.find_parameter('NPT')
        block_float=struct.unpack('i',self.data[self.pointer+5+parameter_index:self.pointer+parameter_index+5+4])[0]
        return block_float
    def xmin(self):
        """Minimum X Value"""
        parameter_index,block_string=self.find_parameter('FXV')
        block_float=struct.unpack('d',self.data[self.pointer+5+parameter_index:self.pointer+parameter_index+5+8])[0]
        return block_float
    def xmax(self):
        """Maximum X Value"""
        parameter_index,block_string=self.find_parameter('LXV')
        block_float=struct.unpack('d',self.data[self.pointer+5+parameter_index:self.pointer+parameter_index+5+8])[0]
        return block_float
    def x_array(self):
        """X Array constructed from xmin, xmax and npts"""
        x_array=linspace(self.xmin(),self.xmax(),self.npts())
        return x_array
        
        
class spectra_data(object):
    """The actual spectra data"""
    def __init__(self,data,pointer,length):
        self.data=data
        self.pointer=pointer
        self.length=length
        self.length_b=4*length
        self.output=dict(y_vals=self.y_vals())
    def y_vals(self):
        y_vals=struct.unpack(str(self.length)+'f',self.data[self.pointer:self.pointer+self.length_b])
        return y_vals

class interferogram_data(object):
    """The interferogram"""
    def __init__(self,data,pointer,length):
        self.data=data
        self.pointer=pointer
        self.length=length
        self.length_b=4*length
        self.output=dict(y_vals=self.y_vals())
    def y_vals(self):
        y_vals=struct.unpack(str(self.length)+'f',self.data[self.pointer:self.pointer+self.length_b])
        return y_vals
         #Can ignore
        
def write_binary(data,pointer,values,filename):
    """Take the original data, replace the values from the pointer onwards, and 
    save it as a new binary file"""
    
    """First pack the new FLOAT values in to binary"""
    input_binary=struct.pack(str(len(values))+"f",*values)
    
    """Create a new binary string containing all the old values with
    new data instead of the original"""
    data_out=data[:pointer]+input_binary+data[pointer+len(input_binary):]
    
    """Write to a new binary file"""
    new_file = open(filename,'wb')
    new_file.write(data_out)
    new_file.close()
    
#        return block_float
        
if __name__=='__main__':
    
    "Lets get to it"
    
    
    """ I did include loads of cool handy argument things that you might want to expand on
    if not, just leave all of this stuff commented"""
    
#    """Loads in a the appropriate arguments from the command line"""
    parser=argparse.ArgumentParser()
    parser.add_argument("file",help="OPUS output file to inspect, must be first!")
    parser.add_argument("-t","--time",help="Output the Time",action="store_true")
    parser.add_argument("-d","--date",help="Output the Date",action="store_true")
    parser.add_argument("-p","--date",help="Output the Date",action="store_true")

    parser.add_argument("-o","--header",help="Output the Opus Header",action="store_true")
    parser.add_argument("-b","--blocks",nargs="+",help="Block names to dump the output of, inst,intf,spec. i.e --blocks intf inst",type=str)

    args=parser.parse_args()
#    
#block_names={'intf':'Interferogram Parameters','inst':'Instrument Parameters','spec':'Spectrum Parameters','intf_data':'Interferogram Data','spec_data':'Spectrum Data'} 
    """Provide file name"""
    filename="test_bnr_2.0"
    #filename=args.file
    
 
    intf_info=None
    inst_info=None
    spectra_info=None
    spectra_dat=None
    intf_dat=None
    
    """Read as binary file"""
    data = file(filename, "rb").read()          
    
    """Get header information - We need to read the header block in the opus file, 
    this tells us what data blocks are present in the file, where they are and how big they are"""    
    header_info=opus_header(data)
    
    """From the header_info get the relevant pieces of information"""
    dir_block_start=header_info.pointer()
    dir_size=header_info.current_size()

    """We can now unpack the directory block based on the head information"""
    block_info=reshape(array(struct.unpack(str(3*dir_size)+'i',data[int(dir_block_start):int(dir_block_start)+3*4*int(dir_size)])    ),newshape=(dir_size,3))

    for i in range(len(block_info)):
        block_info[i][0]=mod(block_info[i][0],2**20)
    """The directory block has 3 int32s for each data block, type, length in 
    words, and pointer. We can use these to go and select the data we want from
    the various different blocks, (parameter or data). I've reshaped the 
    directory info list into the appropriate blocks
    """

    """now we need to go through the block ids and find the pointers and sizes 
    that we want."""
    dispatcher={} #Can ignore
    block_pointer=0
    block_length=0
    for i,j in enumerate(block_info):
        print i, j
        if j[0]==2071 or j[0]==2075:
            block_pointer=j[2]
            block_length=j[1]
            print 'Interferogram Parameters Found'
            intf_info=interferogram_parameters(data,block_pointer,block_length)
            dispatcher['intf']=intf_info.output.items() #Can ignore
        if j[0]==32:
            block_pointer=j[2]
            block_length=j[1]
            print 'Instrument Parameters Found'
            inst_info=instrument_parameters(data,block_pointer,block_length)
            dispatcher['inst']=inst_info.output.items() #Can ignore

        if j[0]==1047 or j[0]==1035:
            block_pointer=j[2]
            block_length=j[1]
            print 'Sample Spectra Parameters Found'
            spectra_info=spectra_parameters(data,block_pointer,block_length)
            dispatcher['spec']=spectra_info.output.items() #Can ignore

        if j[0]==1031 or j[0]==1035:
            block_pointer=j[2]
            block_length=j[1]
            print 'Sample Spectra Data Found'
            spectra_pointer=block_pointer
            spectra_dat=spectra_data(data,block_pointer,block_length)
            dispatcher['spec_data']=spectra_dat.output.items() #Can ignore
        
        if j[0]==2059 or j[0]==2055:
            block_pointer=j[2]
            block_length=j[1]
            print 'Interferogram Data Found'
            intf_dat=interferogram_data(data,block_pointer,block_length)
            dispatcher['intf_data']=intf_dat.output.items() #Can ignore
##  
            
    """Here is some conditional formatting of the observation date and time, we do
    this for historical reasons as some of our files have different formats, i.e do
    not have the spectrum and so we have to pull the date and time from somewhere else,
    in a slightly different format"""
    
    obs_time='None Found'
    obs_date='None Found'
    obs_duration='None Found'
    if intf_info!=None:
        obs_time=intf_info.time()
        obs_date=intf_info.date()
    elif spectra_info!=None:
        obs_time=spectra_info.time()
        obs_time=obs_time.replace(' ','0')
        obs_date=spectra_info.date()
        
        
    if inst_info!=None:
        obs_duration=inst_info.duration()

    """Print the information"""
    
    print 'Time', obs_time
    print 'Date', obs_date
    print 'Duration', obs_duration
    
    """Here is the spectra"""
    plot(spectra_info.x_array(),spectra_dat.y_vals())
    
    
    
    """Example of writing to new binary file"""
    
    """first off lets just take the original spectra and make an obvious change"""
    
    new_spectra=array(spectra_dat.y_vals())
    new_spectra[0:len(new_spectra)/5]=max(new_spectra) 
    
    """Now we can write the new spectra to a new opus file with all of the original
    parameters, you might want to change some but hopefully this is sufficient"""
    
   # write_binary(data,spectra_pointer,new_spectra,"test_output.0")


    
    """We now need to add in some keyword argument switches that return
    various outputs as per dans wishes. I'll keep the printouts above for now
    and the finding of the time and date etc"""
    
#    print "\n"
#    if args.header:
#        print 'Block - Opus Header'
#        for i,j in header_info.output.items():
#            print str(i)+" = "+str(j)
#        print '\n'    
#    if args.time:
#        print 'Time = '+obs_time
#        print '\n'
#    if args.date:
#        print 'Date = '+obs_date
#        print '\n'
#    if args.blocks:
#        for i in range(len(args.blocks)):
#            print "Block - "+str(block_names[args.blocks[i]])
#            try:
#                for k,v in dispatcher[args.blocks[i]]:
#                    print str(k)+" = "+str(v)
#            except:
#                keys_avail=dispatcher.keys()
#                print "Block Unavailable, next time choose from:"
#                for k in range(len(keys_avail)):
#                    print keys_avail[k]
#            print '\n'
#  