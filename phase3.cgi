#!/usr/bin/perl
use lib ((getpwuid($<))[7]) . '/local/lib/perl5';
use strict;
use warnings;
use CGI;
use CGI::Session;
use CGI::Carp qw(fatalsToBrowser); 
use HTML::Template;
use Data::Dumper;
use JSON;
use MIME::Base64;
use SFCON::Register;
use SFCON::Register_db;
use pgreglib;
our %CONDEF_CONST;

my $cgi=CGI->new;
my $register = SFCON::Register->new;
my $database = SFCON::Register_db->new;

# セッションID = urlパラメータ||cookieからCGISESSID||取得できなかったらundef．
my $sid=$cgi->param('ID')||$cgi->cookie('ID')||undef;
my $session=CGI::Session->new(undef,$sid,{Directory=>$register->session_dir()});

my $input_page;
my $http_header;

if(defined $sid && $sid eq $session->id){
    # 取得したセッションidが有効:登録処理
    ##>> テストDB使用
    $database->prefix("test54_");
    ##<< テストDB使用
    my $r_num = sprintf( "%04d", $database->getprogramnumber($sid, 0));
    my $name     = $session->param('p1_name');
    my $mailaddr = $session->param('email');

    # 登録者に送るmail生成/送付
    my $mail_out = HTML::Template->new(filename => 'mail-finish-tmpl.txt');
    pgreglib::pg_stdMailTmpl_set( $mail_out, $mailaddr, $name );
    pgreglib::pg_HtmlTmpl_set($mail_out, $session);
    my $mbody = $mail_out->output;
    pgreglib::doMailSend( $CONDEF_CONST{'ENVFROM'},
                [ $mailaddr, $CONDEF_CONST{'ENTADDR'}, ],
                $mbody );

    # 企画登録スタッフに送るメールの作成/送付
    $mail_out = HTML::Template->new(filename => 'mail-regist-tmpl.txt');
    pgreglib::pg_stdMailTmpl_set( $mail_out, $CONDEF_CONST{'PGSTAFF'}, undef );
    $mail_out->param(BOUNDER    => '_REGPRM_' . $sid . '_');
    $mail_out->param(PGNO       => $r_num);
    $mail_out->param(MIMEPGSG   => $CONDEF_CONST{'MIMEPGS'});
    my $pHreg_param = pgreglib::pg_createRegParam($session, $r_num);
    $Data::Dumper::Terse = 1; # 変数名を表示しないおまじない
    $mail_out->param(REGPRM_DUMP    => Dumper($pHreg_param));
    $mail_out->param(JSON_FNAME     => 'reg_' . $r_num . '.json');
    $mail_out->param(REGPRM_JSON    => encode_base64(encode_json($pHreg_param)));
    my $mbody2 = $mail_out->output;
    pgreglib::doMailSend( $CONDEF_CONST{'ENVFROM'},
                [ $CONDEF_CONST{'PGSTAFF'}, ],
                $mbody2 );
    
    # HTMLを生成する。
    $input_page=HTML::Template->new(filename => 'phase3-tmpl.html');
    pgreglib::pg_HtmlTmpl_set($input_page, $session);
    if ( $session->param('reg_num') eq $CONDEF_CONST{'SPREGNUM2'}) {
        pgreglib::pg_HtmlMailChk_set($input_page, $mbody, $mbody2);
    }
    $http_header = $cgi->header(-charset=>'UTF-8', -expires=>'now');

    # 全処理が完了したのでセッションを削除
    $session->close;
    $session->delete;

}else{
    # 取得したセッションidが無効:エラー画面表示
    # 古いセッションを削除
    if(defined $sid && $sid ne $session->id){
        $session->close;
        $session->delete;
    }
    $input_page=HTML::Template->new(filename => 'error.html');
    $http_header = $cgi->header(-charset=>'UTF-8');
}
# 共通のTMPL変数置き換え
pgreglib::pg_stdHtmlTmpl_set( $input_page, $sid );

print $http_header;
print "\n\n";
print $input_page->output;

exit;

1;
#end
