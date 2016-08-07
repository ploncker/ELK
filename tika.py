__author__ = 'ashmaro1'

def parse_file(filename):
   """
   Import TIKA classes and parse input filename
   """

   import os
   os.environ['CLASSPATH'] = "/path/to/tika-app.jar"
   from jnius import autoclass
   from jnius import JavaException

   # Import the Java classes
   Tika = autoclass('org.apache.tika.Tika')
   Metadata = autoclass('org.apache.tika.metadata.Metadata')
   FileInputStream = autoclass('java.io.FileInputStream')

   tika = Tika()
   tika.setMaxStringLength(10*1024*1024);
   meta = Metadata()

   # Raise an exception and continue if parsing fails
   try:
       text = tika.parseToString(FileInputStream(filename), meta)
       return text
   except (JavaException,UnicodeDecodeError), e:
       print "ERROR: %s" % (e)
   return None


if __name__ == "__main__":

    #import subprocess
    #subprocess.call(['java', '-jar', 'C:/Program Files/Tika/tika-app-1.13.jar'])

    #from tika import parser
    #start thr tika server and listen on port 9998
    # from command line: java -jar tika-server-1.13.jar --port 9998
    import tika
    tika.TikaClientOnly = True
    from tika import parser
    #parsed = parser.from_file("C:/Users/ashmaro1/Documents/Literature/Predicting customer retention random forrests.pdf",
    #                          'http://localhost:9998')
    parsed = parser.from_file("C:/Users/ashmaro1/Documents/_Projects/Glencore/POxca-000052-R201631.pdf",
                              'http://localhost:9998')
    print '#------------------'
    print parsed["metadata"]
    print parsed["content"]
