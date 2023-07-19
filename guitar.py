import fretboard  

#First define notes
notes = ['c','c#','d','d#','e','f','f#','g','g#','a','a#','b','c','c#','d','d#','e','f','f#','g','g#','a','a#','b']

scale_dict = {
    'maj_scale':[0,2,4,5,7,9,11],
    'min_scale':[0,2,3,5,7,8,10],
    'minpent_scale': [0,3,5,7,10],
    'majpent_scale': [0,2,4,7,9],
    'mixylodian_scale': [0,2,4,5,7,9,10],
    'chromatic': [0,1,2,3,4,5,6,7,8,9,10,11],
    'maj_arp':[0,4,7] ,
    'min_arp':[0,3,7]
}

string = [0,1,2,3,4,5,6,7,8,9,10,11]

class Guitar:
        
    def scale(self,root,scalelist):
        scale_ls=scale_dict[scalelist]
        a=notes.index(root)
        note_ls = []
        for i in (scale_ls):
            note_ls.append(notes[a+i]) 
        return note_ls
    
    def stringdef(self,root):
        scale_ls=scale_dict['chromatic']
        a=notes.index(root)
        note_ls = []
        for i in (scale_ls):
            note_ls.append(notes[a+i]) 
        return note_ls
    
    def Notes_on_String2(self,root,scalelist,stringnum):
        string_ls = self.stringdef(stringnum)
        note_ls = self.scale(root,scalelist)
        fret_ls = []
        for i in note_ls:
            fret_ls.append(string_ls.index(i))
        fret_ls.sort()   
        return fret_ls
    
    def full_fretboard(self,root,scale,tuning):
        count=0
        for t in tuning:
            count+1
            results=self.Notes_on_String2(root,scale,t)
        return results

    def note_labels(self,root,scale,tuning,count):
        for t in tuning:
            count = count + 1
            results=self.Notes_on_String2(root,scale,t)
            note_ls = []
            fret_ls = []
            for fret in results:
                offset=notes.index(t)+fret  
                fret_ls.append(fret)
                note_ls.append(notes[offset])
        return note_ls
    
    def add_markers(self,root,scale,tuning,count):
        marker_ls = []
        for t in tuning:
            count=count+1
            results=self.Notes_on_String2(root,scale,t)
            for r in results:
                offset=notes.index(t)+r     
                marker_ls.append([count-1,r,notes[offset]])
        return marker_ls
                  
    def draw_fretboard(self,fretlow,frethigh,root,scale,tuning,count,svg_file):
        fb = fretboard.Fretboard(frets=(fretlow,frethigh), style={'drawing': {                                                                              'width': 400,
                                                                                'height':500},
                                                                    'marker': {'color': 'black'},})
        marker = self.add_markers(root,scale,tuning,count)
        for m in marker:
            if m[1] >= fretlow:
                if m[2] == root  :
                    fb.add_marker(string=m[0], fret=m[1],label=m[2],color='blue')
                    fb.add_marker(string=m[0], fret=m[1]+12,label=m[2],color='blue')
                else:
                    fb.add_marker(string=m[0], fret=m[1],label=m[2])
                    fb.add_marker(string=m[0], fret=m[1]+12,label=m[2])
        fb.save(svg_file)  
   
    def get_svg_string(self,svg_file):
        with open(svg_file, "r") as file:
            svg_string = file.read()
        return svg_string
    
    # def display_svg(self,svg_string):
    #     display(SVG(svg_string))