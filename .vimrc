:command! AutoformatPython w | silent execute "!isort % -l 120 -m 0" | silent execute "!autoflake --in-place -rc %" | silent execute "!black %" | redraw! | :e | :PymodeLint
:autocmd! BufWritePost *.py :AutoformatPython

let g:pymode_options_max_line_length = 100
let g:pymode_breakpoint_cmd = '__import__("ipdb").set_trace()'

let g:pymode_options_colorcolumn = 0
let &colorcolumn="80,".join(range(121,999),",")
