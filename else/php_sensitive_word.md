## php 敏感关键字

### 数据库操作

    mysql_connect
    mysql_query
    mysql_fetch_row
    mysql_set_charset

    addslashes
    mysql_escape_string
    mysql_real_escape_string

### 文件操作

    include
    include_once
    require
    require_once

    file_get_contents
    readfile
    highlight_file
    show_source
    fopen
    fread
    fgets
    fgetss
    parse_ini_file
    file

    unlink

### 代码执行

    eval
    assert
    call_user_func
    call_user_func_array
    array_map
    array_reduce
    array_filter
    preg_replace    #php<5.4

### 命令执行

    system
    exec
    shell_exec
    passthru
    pcntl_exec
    popen
    proc_open
    反引号`

    escapeshellcmd
    escapeshellarg

### 全局

    extract
    parse_str
    import_request_variables    #php<=5.4

### 其他

    iconv   #字符编码转换，可能会造成截断，例如iconv("UTF-8","gbk",$a)，如果$a='1'.chr(130).'2'，则截断为1
    mb_convert_encoding($sql,"UTF-8","GBK") #%df%5c' 会被截断
    $$      #可能存在变量覆盖