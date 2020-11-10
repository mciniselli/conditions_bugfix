
import codecs
import os
import sys

result_path = 'raw_data/bugfix.txt'
num_chunks=10


def ReadFile(filepath): # read generic file
    try:
        with open(filepath, encoding="utf-8") as f:
            content=f.readlines()
        c_=list()
        for c in content:
            r=c.rstrip("\n").rstrip("\r")
            c_.append(r)

    except Exception as e:
        print("Error ReadFile: " + str(e) )
        c_=[]
    return c_

def WriteFile(filename, list_item): #write generic file
    file = codecs.open(filename, "w", "utf-8")

    for line in list_item:
        file.write(line+"\n")

    file.close()


def main():
	records=ReadFile(result_path)
	print("NUM RECORDS: {}".format(len(records)))

	batch_size=len(records) // num_chunks

	print("BATCH SIZE: {}".format(batch_size))

	for i in range(num_chunks):
		start=i*batch_size
		end=(i+1)*batch_size
		print("START {} END {}".format(start, end))
		if i==num_chunks-1:
			end=len(records)

		WriteFile(result_path.replace(".txt", "_{}.txt".format(i)), records[start:end])



def Create_Fake_Result(n):

	list_items=list()

	if os.path.exists("result")==False:
		os.makedirs("result")

	for i in range(n):
		list_items.append("{} {} {}".format(i, i-3, i*4))

	WriteFile(result_path, list_items)



if __name__ == "__main__":

    if len(sys.argv)==3:
        result_path=sys.argv[1]
        num_chunks=int(sys.argv[2])

    #Create_Fake_Result(1014)
    main()
