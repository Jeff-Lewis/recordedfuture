#Copyright (c) 2010, Recorded Future, Inc.
#All rights reserved.

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Recorded Future nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL RECORDED FUTURE, INC. BE LIABLE FOR ANY
#DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
This module contains several functions for accessing the Recorded Future API from Python.
'''


import urllib, json, datetime, zlib, sys, time


def query(q, usecompression=True):
	"""
	Issue a JSON-formatted query against the Recorded Future web service
	and return a dict corresponding to the JSON object returned as a result
	of that query.
	"""
	try:
		url = 'http://api.recordedfuture.com/ws/rfq/instances?%s'

		if usecompression:
			url = url + '&compress=1'
			
		for i in range(3):
			try:
				data = urllib.urlopen(url % urllib.urlencode({"q":q}))

				if type(data) != str:
					data = data.read()

				if usecompression:
					data = zlib.decompress(data)
				break
			except:
				print >>sys.stderr, "Retrying failed API call."
				time.sleep(1)
				
        #print data
		return json.loads(data)
	except Exception, e:
		print str(e)
		return {'status': 'FAILURE', 'errors': str(e)}


def daterange(start, stop, step=datetime.timedelta(days=1), inclusive=False):
  	"""Produce a range of dates given start and end date and optionally step size."""
	# inclusive=False to behave like range by default
	if step.days > 0:
	  while start < stop:
	    yield start
	    start = start + step
	    # not +=! don't modify object passed in if it's mutable
	    # since this function is not restricted to
	    # only types from datetime module
	elif step.days < 0:
	  while start > stop:
	    yield start
	    start = start + step
	if inclusive and start == stop:
	  yield start


def flatten_dict(d):
	"""Produce a flattened list of key-value pairs from a nested dictionary."""
	res={}
	for k,v in d.items():
		if isinstance(v,dict):
			subdict=flatten_dict(v)
			for subk,subv in subdict.items():
				res[k+'.'+subk]=subv
		else:
			res[k]=v
	return res

def parse_value(val,entities):
	"""
	Parse either a value or list of values and return combined results free
	of tab and newline characters.
	"""
	if unicode(val) in entities:
		val=entities[unicode(val)]['name']
		val=''.join([c for c in val if ord(c)<128])
		return val.replace('\n',' ').replace('\t',' ').strip()
	elif isinstance(val,unicode):
		val=''.join([c for c in val if ord(c)<128])
		return val.replace('\n',' ').replace('\t',' ').strip()
	else:
		return val


def flatten_query(q, outputorder=False):
	"""Run a query against the Recorded Future API and flatten the results
	into a list of tab-delimited rows. Useful for producing datasets from 
	query results. The optional outputorder argument specifies which columns
	to include in output and in which order they should appear."""
	result = query(q)

	if result['status']=='FAILURE':
		print 'FAILURE'
		print result['errors'][0]
		#print result['stacktrace'].replace('\n',' ')
		sys.exit(1)
	elif 'count' in result:
		print 'COUNT'
		print result['count']
		sys.exit(0)

	if 'entities' in result:
		entities=result['entities']
	else:
		entities={}

	output_data=[]
	if 'instances' in result:
		output_data=result['instances']
	elif 'sources' in result:
		output_data=result['sources']
	elif 'entity_details' in result:
		output_data=[]
		for key,val in result['entity_details'].items():
			val['id']=key
			output_data.append(val)

	if not outputorder:
		headers=[]
		for instance in output_data:
			flat_instance=flatten_dict(instance)
			headers+=[k for k in flat_instance if k not in headers]

		if "document.id" in headers:
			headers=['document.id']+[h for h in headers if h!='document.id']
	else:
		headers = outputorder

	rows=[]
	for instance in output_data:
		flat_instance=flatten_dict(instance)
		newrow=[]
		for col in headers:
			if col in flat_instance:
				val=flat_instance[col]
				if isinstance(val,list):
					newrow.append(','.join([unicode(parse_value(v,entities)) for v in val]))
				else:
					newrow.append(parse_value(val,entities))
			else:
				newrow.append(' ')

		rows.append(newrow)

	retrows = []
	retrows.append('\t'.join(headers))
	for row in rows:
		retrows.append('\t'.join(['"'+v if isinstance(v,unicode) else str(v) for v in row]))

	return retrows

def lookup_id(ticker, token):
        idtickers = {"ABT":33312109,"ANF":33559171,"ADBE":33312868,"AMD":33331720,"AES":33865842,
						"AET":33376265,"ACS":39385922,"AFL":33838067,"A":33989748,"APD":33963099,
						"AKAM":33468828,"AKS":34828923,"AA":33395365,"AYE":33347000,"ATI":34020013,
					    "AGN":33349977,"ALL":34508653,"ALTR":33323928,"MO":33330611,"AMZN":33328212,
						"AEE":34254695,"AEP":33330626,"AXP":33354969,"AIG":33350361,"AMT":40830099,
						"AMP":33412940,"ABC":34201178,"AMGN":33339480,"APC":33750985,"ADI":33584019,
						"AON":33436919,"APA":33545389,"AIV":36573549,"APOL":33350645,"AAPL":33340558,
						"AMAT":33350155,"ADM":33487566,"ASH":33516345,"AIZ":35576017,"T":33315638,
						"ADSK":33465524,"ADP":34430684,"AN":33323081,"AZO":34345927,"AVB":37394306,
						"AVY":40378169,"AVP":34648562,"BHI":33878511,"BLL":35654025,"BAC":33341412,
						"BK":33391430,"BCR":34201174,"BAX":33702897,"BBT":33415054,"BDX":33333503,
						"BBBY":35385330,"BMS":33336296,"BBY":33359526,"BIG":34232065,"BIIB":33343716,
						"BJS":33315447,"BDK":33338509,"HRB":33400581,"BMC":33335057,"BA":33318950,
						"BXP":36960799,"BSX":33902441,"BMY":33685285,"BRCM":33410029,"BF.B":34485469,
						"BNI":33510636,"CHRW":40625159,"CA":33335975,"COG":40630511,"CAM":42716610,
						"CPB":33450075,"COF":33494789,"CAH":33336044,"CFN":40188087,"CCL":35044941,
						"CAT":33340704,"CBG":33447285,"CBS":33345617,"CELG":33628136,"CNP":36966411,
						"CTL":33337600,"CEPH":33348763,"CF":37089960,"SCHW":33527322,"CHK":33511577,
						"CVX":33347211,"CB":33588341,"CIEN":33733196,"CI":34544759,"CINF":34950400,
						"CTAS":37283169,"CSCO":33321670,"C":33316351,"CTXS":33339446,"CLX":33334434,
						"CME":33504138,"CMS":33333445,"COH":33603544,"KO":33316334,"CCE":33323094,
						"CTSH":33678869,"CL":33662491,"CMCSA":33347800,"CMA":33845402,"CSC":35675477,
						"CPWR":34210938,"CAG":34448381,"COP":33324657,"CNX":33604669,"ED":33597046,
						"STZ":34232030,"CEG":33851387,"CVG":33520708,"CBE":33338392,"GLW":33336032,
						"COST":33700907,"CVH":38910974,"CSX":33363281,"CMI":33347609,"CVS":33349178,
						"DHI":34622704,"DHR":33604524,"DRI":33937079,"DVA":33591859,"DF":33333817,
						"DE":33564841,"DELL":33326108,"DNR":34630919,"XRAY":42275425,"DVN":33345324,
						"DV":47621128,"DO":33971024,"DTV":33479092,"DFS":33565694,"D":34476891,
						"RRD":43984936,"DOV":33418598,"DOW":33350181,"DPS":41334584,"DTE":34203402,
						"DD":33341099,"DUK":33332067,"DNB":33334879,"DYN":33344423,"ETFC":35208690,
						"EMN":39035287,"EK":33412523,"ETN":33330038,"EBAY":33323059,"ECL":33338303,
						"EIX":33928248,"EP":33391384,"ERTS":33312055,"EMC":33321640,"EMR":33756213,
						"ETR":33652331,"EOG":33346558,"EQT":35566420,"EFX":33400914,"EQR":36960835,
						"EL":33396385,"EXC":34103705,"EXPE":33348628,"EXPD":40830102,"ESRX":33335013,
						"XOM":33348656,"FDO":33937171,"FAST":40478108,"FII":33906038,"FDX":33380156,
						"FIS":33420386,"FITB":33440277,"FHN":40224555,"FSLR":33397875,"FE":34582654,
						"FISV":33336189,"FLIR":33828508,"FLS":44523727,"FLR":34737142,"FMC":33336092,
						"FTI":35072065,"F":33316011,"FRX":34053223,"FO":33387412,"FPL":33337526,
						"BEN":33870382,"FCX":37487623,"FTR":40266308,"GME":33348007,"GCI":33321240,
						"GPS":34190682,"GD":33334515,"GE":33335480,"GIS":33488598,"GPC":42669425,
						"GNW":35594597,"GENZ":33339759,"GILD":33324304,"GS":33323977,"GR":33398533,
						"GT":37616530,"GOOG":33321272,"GWW":41468163,"HAL":33313096,"HOG":33371871,
						"HAR":33959672,"HRS":33335969,"HIG":33604451,"HAS":33355099,"HCP":34653914,
						"HCN":33780018,"HNZ":33611188,"HES":34499787,"HPQ":179647470,"HD":33325283,
						"HON":33326581,"HRL":34470370,"HSP":33333410,"HST":35049176,"HCBK":33564159,
						"HUM":33397455,"HBAN":33401003,"ITW":34814864,"RX":33555581,"TEG":41743091,
						"INTC":33321371,"ICE":33504117,"IBM":33314966,"IFF":44070143,"IGT":35698071,
						"IP":35210411,"IPG":40020576,"INTU":33438411,"ISRG":33644026,"IVZ":40956670,
						"IRM":33335664,"ITT":33338513,"JBL":38895117,"JEC":42579634,"JNS":33667714,
						"JDSU":33335774,"JNJ":33331958,"JCI":33356013,"JPM":33335403,"JNPR":33403089,
						"KBH":33516367,"K":33336003,"KEY":33354887,"KMB":33391770,"KIM":35908509,
						"KG":33459136,"KLAC":36134719,"KSS":33332623,"KFT":33432816,"KR":34076534,
						"LLL":33344390,"LH":33579408,"LM":34168826,"LEG":33323812,"LEN":33673244,
						"LUK":33512956,"LXK":33341069,"LIFE":33790036,"LLY":33458193,"LTD":34492743,
						"LNC":33350642,"LLTC":39984515,"LMT":33334580,"L":33589242,"LO":33361634,
						"LOW":33518999,"LSI":33421820,"MTB":33399838,"M":33388377,"MRO":33374962,
						"MAR":33473008,"MMC":34260325,"MI":33604062,"MAS":34362365,"MEE":33347873,
						"MA":33488122,"MAT":33484239,"MBI":33520675,"MFE":33538377,"MKC":33333338,
						"MCD":33318955,"MHP":33336373,"MCK":33336186,"MWV":33361605,"MHS":33333482,
						"MDT":33555172,"WFR":38761722,"MRK":33332022,"MDP":33336012,"MET":33436978,
						"PCS":39716491,"MCHP":45775465,"MU":33686536,"MSFT":33312449,"MIL":41298134,
						"MOLX":33323945,"TAP":33334611,"MON":33334926,"MWW":36590465,"MCO":42880618,
						"MS":33318593,"MOT":33329907,"MUR":33393894,"MYL":33518880,"NBR":33351419,
						"NDAQ":35079783,"NOV":33535240,"NSM":33965564,"NTAP":33595526,"NYT":33321211,
						"NWL":33335643,"NEM":33350537,"NWSA":33344031,"GAS":34657411,"NKE":33342128,
						"NI":33333754,"NBL":33413550,"JWN":33332531,"NSC":33354510,"NTRS":33354368,
						"NOC":33354777,"NU":39424174,"NOVL":33462640,"NVLS":34282118,"NUE":33535321,
						"NVDA":33312648,"NYX":33323470,"ORLY":36959136,"OXY":33604116,"ODP":33480649,
						"OMC":34207403,"ORCL":33320806,"OI":33564241,"PCAR":33565644,"PTV":33341102,
						"PLL":39637891,"PH":41344174,"PDCO":42728599,"PAYX":35081607,"BTU":33960028,
						"JCP":33483372,"PBCT":33312176,"POM":33899569,"PBG":33330608,"PEP":33312704,
						"PKI":36959693,"PFE":33343257,"PCG":33332652,"PM":33499561,"PNW":33392852,
						"PXD":34060396,"PBI":33333967,"PCL":33433318,"PNC":33370522,"RL":37358585,
						"PPG":40753961,"PPL":33333721,"PX":33823899,"PCP":44426185,"PCLN":33388875,
						"PFG":34077292,"PG":33335184,"PGN":33334492,"PGR":43754665,"PLD":33338372,
						"PRU":33349737,"PEG":36646044,"PSA":33342142,"PHM":33353997,"QLGC":34624556,
						"PWR":33333490,"QCOM":33330620,"DGX":33335472,"STR":35052502,"Q":33470871,
						"RSH":33353831,"RRC":33962980,"RTN":33334411,"RHT":33321899,"RF":33584492,
						"RSG":36959698,"RAI":33397227,"RHI":33604053,"ROK":34082249,"COL":33334383,
						"ROP":43484091,"RDC":33346095,"R":33339793,"SWY":33344556,"CRM":33681747,
						"SNDK":33338113,"SLE":33345387,"SCG":33348760,"SLB":33564184,"SNI":42043298,
						"SEE":34838181,"SHLD":33479348,"SRE":33551577,"SHW":33524108,"SIAL":33340333,
						"SPG":33667940,"SLM":33571719,"SII":38947323,"SJM":41925014,"SNA":33323992,
						"SO":33946153,"LUV":33435627,"SWN":34981119,"SE":34131568,"S":33337802,
						"STJ":36540214,"SWK":33340937,"SPLS":33335854,"SBUX":33368388,"HOT":33902879,
						"STT":33323461,"SRCL":42733353,"SYK":37094423,"JAVA":33321598,"SUN":33323246,
						"STI":33576235,"SVU":33323249,"SYMC":33312357,"SYY":33651550,"TROW":33351728,
						"TGT":33487836,"TE":33335551,"TLAB":33340803,"THC":33859653,"TDC":37409618,
						"TER":33417764,"TSO":33644908,"TXN":33328438,"TXT":35080317,"HSY":33534606,
						"TRV":33643987,"TMO":33531796,"TIF":33480130,"TWX":33323010,"TWC":33497353,
						"TIE":39425969,"TJX":33332676,"TMK":33323871,"TSS":41813356,"TSN":33356680,
						"USB":33323367,"UNP":33603119,"UNH":33489182,"UPS":33579817,"X":34363260,
						"UTX":33323354,"UNM":34367128,"VFC":35336890,"VLO":33351102,"VAR":33312227,
						"VTR":33333517,"VRSN":33340565,"VZ":33319391,"VIA":33462927,"VNO":40232807,
						"VMC":33333091,"WMT":33329965,"WAG":33311734,"DIS":33536283,"WPO":33325868,
						"WM":33534833,"WAT":33974638,"WPI":33935184,"WLP":33323995,"WFC":33319369,
						"WDC":33402385,"WU":33328199,"WY":34643156,"WHR":34155199,"WFMI":33511548,
						"WMB":33323438,"WIN":33341594,"WEC":33350456,"WYN":34024279,"WYNN":33410968,
						"XEL":33338704,"XRX":33353148,"XLNX":33584058,"XL":34361699,"XTO":33345178,
						"YHOO":33312849,"YUM":33323839,"ZMH":39850415,"ZION":43956818,"WYE":33340018,
						"WB":208820320,"RIG":33345344,"MER":33325146,"BUD":33649109,"SGP":33354867,
						"WFT":41726511,"FNM":33331158,"COV":40603049,"TYC":35505618,"ACE":33335986,
						"LEH":36989386,"TEL":33771992,"CCU":199793805,"NE":33625523,"WWY":33544753,
						"FRE":33312338,"AOC":33436919,"EDS":199796653,"IR":33323998,"GGP":33373719,
						"ESV":33604571,"GM":33316013,"UST":199802928,"TT":33967914,"EQ":33335658,
						"TEX":33386837,"ROH":33361543,"ACAS":34206777,"SAF":33690856,"ABI":73695590,
						"MTW":34025020,"DDR":34071264,"AW":61915210,"SOV":33506803,"NCC":33515100,
						"SSP":34443549,"IACI":33587736,"CZN":208811440,"CFC":33471876,"CIT":33343468,
						"WEN":38640530,"HPC":33340570,"CTX":33661855,"UIS":34487503,"LIZ":33749522,
						"OMX":33480585,"MTG":35770097,"JNY":34018659,"BSC":33331167,"BC":34546774,
						"DDS":33332528,"ABK":42517032,"MMM":33334336}

        if idtickers.get(ticker):
                return [int(idtickers.get(ticker))]

        idquery = """{
                "entity":   {
                  "type": "Company",
                  "attributes": {"name": "tickers", "string": "C"}
                },
                "output": {"fields":   [
                 "id",
                 "attributes"
                ]},
                "token": ""
                }"""

        tickerdict = ""
        iddict = json.loads(idquery)
        iddict["token"] = token
        iddict["entity"]["attributes"]["string"] = ticker
        res = query(q = json.dumps(iddict))

        return res["entities"]
